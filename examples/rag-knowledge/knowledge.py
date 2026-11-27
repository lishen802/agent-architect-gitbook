"""Chapter 9 teaching example: a permission-aware hybrid retriever and evidence checks.

Everything here is standard library only. The "vectors" in ``scenario.json`` are
hand-written teaching fixtures that stand in for an embedding model's output; their
eight dimensions have names only so that a reader can follow the example. Real
embedding dimensions carry no such labels, and query and chunk vectors must come
from the same embedding model.
"""
import math
import re
from collections import Counter
from dataclasses import dataclass, field

ASCII_TOKEN = re.compile(r'[a-z0-9_]+(?:[-.][a-z0-9_]+)*')
CJK = re.compile(r'[\u4e00-\u9fff]+')


def tokenize(text):
    """Lowercased ASCII words (keeping identifiers such as ``pay-504``) plus CJK bigrams.

    Character bigrams are a common baseline for Chinese without a word segmenter;
    a production index would use an analyzer chosen and evaluated for its language.
    """
    text = text.lower()
    tokens = ASCII_TOKEN.findall(text)
    for run in CJK.findall(text):
        if len(run) == 1:
            tokens.append(run)
        tokens.extend(run[i:i + 2] for i in range(len(run) - 1))
    return tokens


@dataclass
class Chunk:
    id: str
    doc_id: str
    doc_version: int
    title: str
    text: str
    tenant: str
    acl: list
    status: str              # published | draft | archived
    service: str             # a service name, or '*' for general guidance
    kind: str                # runbook | postmortem
    vector: list
    applies_to: str = ''     # major version the runbook was written for, e.g. '3'
    tokens: list = field(default_factory=list, repr=False)

    def __post_init__(self):
        self.tokens = tokenize(self.title + ' ' + self.text)


def visible(chunk, ctx):
    """Permission and lifecycle filter, evaluated before ranking (pre-filtering).

    The tenant and groups come from the authenticated request context, never from
    the question text or the model.
    """
    return (chunk.tenant == ctx['tenant']
            and bool(set(chunk.acl) & set(ctx['groups']))
            and chunk.status == 'published')


class Index:
    """In-memory index holding chunks, BM25 statistics and vectors."""

    def __init__(self, chunks, k1=1.2, b=0.75):
        self.k1, self.b = k1, b       # Lucene / Elasticsearch BM25 defaults
        self.chunks = {}
        for c in chunks:
            self.chunks[c.id] = c
        self._stats()

    def _stats(self):
        self.df = Counter()
        for c in self.chunks.values():
            self.df.update(set(c.tokens))
        self.n = len(self.chunks)
        self.avgdl = sum(len(c.tokens) for c in self.chunks.values()) / max(self.n, 1)

    # ---- freshness: the index follows source changes by document ----------
    def apply_change(self, event, new_chunks=()):
        """Apply a source-system change. Update and delete act on every chunk of the
        document, so no orphan chunk from an older version stays searchable."""
        doc = event['doc_id']
        stale = [cid for cid, c in self.chunks.items() if c.doc_id == doc]
        for cid in stale:
            del self.chunks[cid]
        if event['op'] == 'upsert':
            for c in new_chunks:
                assert c.doc_id == doc and c.doc_version == event['version'], 'chunk does not belong to this change'
                self.chunks[c.id] = c
        elif event['op'] != 'delete':
            raise ValueError(event['op'])
        self._stats()
        return len(stale)

    def stale_chunks(self, source_versions):
        """Chunks whose document version differs from the source registry, or whose
        document no longer exists there. Run it after every sync as a freshness check."""
        return sorted(cid for cid, c in self.chunks.items()
                      if source_versions.get(c.doc_id) != c.doc_version)

    # ---- retrieval ------------------------------------------------------
    def bm25(self, query, ctx, k):
        q = tokenize(query)
        scores = []
        for c in self.chunks.values():
            if not visible(c, ctx):
                continue
            tf = Counter(c.tokens)
            s = 0.0
            for t in set(q):
                if t not in tf:
                    continue
                idf = math.log(1 + (self.n - self.df[t] + 0.5) / (self.df[t] + 0.5))
                f = tf[t]
                s += idf * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * len(c.tokens) / self.avgdl))
            if s > 0:                 # lexical retrieval returns only chunks that share a term
                scores.append((round(s, 4), c.id))
        scores.sort(key=lambda x: (-x[0], x[1]))
        return [cid for _, cid in scores[:k]]

    def vector(self, qvec, ctx, k, min_similarity=0.5, prefilter=True):
        """Exact cosine search. ``prefilter=False`` shows the post-filtering pitfall:
        the top k is taken first, then invisible chunks are discarded."""
        scored = []
        for c in self.chunks.values():
            if prefilter and not visible(c, ctx):
                continue
            s = cosine(qvec, c.vector)
            if s >= min_similarity:
                scored.append((round(s, 4), c.id))
        scored.sort(key=lambda x: (-x[0], x[1]))
        top = [cid for _, cid in scored[:k]]
        if not prefilter:
            top = [cid for cid in top if visible(self.chunks[cid], ctx)]
        return top


def cosine(a, b):
    assert len(a) == len(b), 'query and chunk vectors must come from the same embedding model'
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def rrf(rankings, k=60, size=None):
    """Reciprocal rank fusion: score(d) = sum over lists of 1 / (k + rank), rank from 1."""
    score = Counter()
    for ranking in rankings:
        for rank, cid in enumerate(ranking, start=1):
            score[cid] += 1.0 / (k + rank)
    fused = sorted(score, key=lambda cid: (-score[cid], cid))
    return fused[:size] if size else fused


def select_evidence(index, ids, scope):
    """Evidence applicability check by metadata. Returns (evidence, excluded, status).

    A chunk is applicable when it is about the service in the task scope (or is
    general guidance), and a runbook written for a major version matches the
    running version. Whether the text actually answers the question still needs
    a reranker, the model, or a human; this check only removes material that
    cannot apply.
    """
    evidence, excluded = [], []
    for cid in ids:
        c = index.chunks[cid]
        if c.service not in (scope['service'], '*'):
            excluded.append((cid, 'service_mismatch'))
        elif c.applies_to and not scope['version'].startswith(c.applies_to + '.'):
            excluded.append((cid, 'version_mismatch'))
        else:
            evidence.append(cid)
    status = 'answerable' if evidence else 'insufficient_evidence'
    return evidence, excluded, status


def check_citations(answer, context_ids, index):
    """Program-checkable part of grounding. Each claim must cite chunks that were in
    the context, each quote must appear verbatim in its chunk, and every number in
    the claim must appear in one of its quotes. Passing these checks does not
    prove the quote supports the claim; that needs semantic judgment."""
    issues = []
    for i, claim in enumerate(answer['claims']):
        cites = claim.get('cites', [])
        if not cites:
            issues.append((i, 'no_citation'))
            continue
        quotes = []
        for cite in cites:
            if cite['chunk'] not in context_ids:
                issues.append((i, 'cited_chunk_not_in_context'))
            elif cite['quote'] not in index.chunks[cite['chunk']].text:
                issues.append((i, 'quote_not_found'))
            else:
                quotes.append(cite['quote'])
        for num in re.findall(r'\d+(?:\.\d+)?', claim['text']):
            if quotes and not any(num in q for q in quotes):
                issues.append((i, 'number_not_in_quote'))
                break
    return issues
