"""Retrieval metrics computed per question; aggregation keeps the denominator visible."""


def recall_at_k(ranked, relevant, k):
    """Share of the labelled relevant chunks that appear in the top k."""
    if not relevant:
        raise ValueError('recall is undefined for a question without labelled evidence')
    return len(set(ranked[:k]) & set(relevant)) / len(relevant)


def reciprocal_rank(ranked, relevant):
    """1 / rank of the first relevant chunk; 0 when none is retrieved."""
    for rank, cid in enumerate(ranked, start=1):
        if cid in relevant:
            return 1.0 / rank
    return 0.0
