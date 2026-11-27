"""Run the chapter 9 scenario: BM25, vector and hybrid retrieval, evidence checks and metrics."""
import json
from pathlib import Path

from knowledge import Chunk, Index, rrf, select_evidence
from metrics import recall_at_k, reciprocal_rank

ROOT = Path(__file__).resolve().parent


def load(path=ROOT / 'scenario.json'):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    return data, Index([Chunk(**c) for c in data['chunks']])


def run(data, index):
    s, ctx = data['settings'], data['context']
    rows, totals = [], {'bm25': [], 'vector': [], 'hybrid': []}
    for q in data['questions']:
        lists = {
            'bm25': index.bm25(q['question'], ctx, s['per_retriever_k']),
            'vector': index.vector(q['vector'], ctx, s['per_retriever_k'], s['min_similarity']),
        }
        lists['hybrid'] = rrf([lists['bm25'], lists['vector']], k=s['rrf_k'], size=s['fused_size'])
        evidence, excluded, status = select_evidence(index, lists['hybrid'], q['scope'])
        row = {'id': q['id'], 'question': q['question'], **lists,
               'evidence': evidence, 'excluded': [list(e) for e in excluded], 'status': status,
               'status_ok': status == q['expect']}
        if q['relevant']:
            row['metrics'] = {}
            for name in ('bm25', 'vector', 'hybrid'):
                r = recall_at_k(lists[name], q['relevant'], s['metric_k'])
                rr = reciprocal_rank(lists[name], q['relevant'])
                row['metrics'][name] = {'recall@%d' % s['metric_k']: round(r, 3), 'rr': round(rr, 3)}
                totals[name].append((r, rr))
            row['evidence_recall'] = round(len(set(evidence) & set(q['relevant'])) / len(q['relevant']), 3)
        rows.append(row)
    summary = {name: {'questions': len(v),
                      'mean_recall@%d' % s['metric_k']: round(sum(r for r, _ in v) / len(v), 3),
                      'mrr': round(sum(rr for _, rr in v) / len(v), 3)}
               for name, v in totals.items()}
    summary['status_ok'] = '%d/%d' % (sum(r['status_ok'] for r in rows), len(rows))
    return {'questions': rows, 'summary': summary}


if __name__ == '__main__':
    data, index = load()
    print(json.dumps(run(data, index), ensure_ascii=False, indent=2))
