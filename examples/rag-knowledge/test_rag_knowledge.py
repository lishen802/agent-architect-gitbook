import copy
import json
import unittest
from pathlib import Path

from demo import load, run
from knowledge import Chunk, Index, check_citations, rrf, select_evidence, tokenize, visible
from metrics import recall_at_k, reciprocal_rank

HERE = Path(__file__).resolve().parent


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.data, self.index = load()
        self.ctx = self.data['context']
        self.model = self.data['settings']['embedding_model']

    def test_report_matches_saved_file_and_chapter(self):
        report = run(self.data, self.index)
        saved = json.loads((HERE / 'report.json').read_text(encoding='utf-8'))
        self.assertEqual(report, saved)
        s = report['summary']
        self.assertEqual((s['bm25']['mean_recall@4'], s['vector']['mean_recall@4'], s['hybrid']['mean_recall@4']),
                         (0.875, 0.75, 1.0))
        self.assertEqual((s['bm25']['mrr'], s['vector']['mrr'], s['hybrid']['mrr']), (0.75, 0.583, 0.625))
        self.assertEqual(s['status_ok'], '5/5')

    def test_tokenizer_keeps_identifiers_and_cjk_bigrams(self):
        self.assertEqual(tokenize('PAY-504 连接池'), ['pay-504', '连接', '接池'])
        self.assertIn('max_pool_size', tokenize('修改 max_pool_size'))

    def test_identifier_needs_lexical_and_paraphrase_needs_vector(self):
        q1, q2 = self.data['questions'][0], self.data['questions'][1]
        k = self.data['settings']['per_retriever_k']
        self.assertIn('RB-30#1', self.index.bm25(q1['question'], self.ctx, k))
        self.assertNotIn('RB-30#1', self.index.vector(q1['vector'], self.model, self.ctx, k))
        self.assertNotIn('RB-12#2', self.index.bm25(q2['question'], self.ctx, k))
        self.assertIn('RB-12#2', self.index.vector(q2['vector'], self.model, self.ctx, k))

    def test_rrf_scores_follow_the_formula(self):
        scores = dict(rrf([['a', 'b'], ['b', 'c']], k=60))
        self.assertAlmostEqual(scores['b'], 1 / 62 + 1 / 61)
        self.assertAlmostEqual(scores['a'], 1 / 61)
        self.assertAlmostEqual(scores['c'], 1 / 62)
        self.assertEqual([d for d, _ in rrf([['a', 'b'], ['b', 'c']], k=60)], ['b', 'a', 'c'])
        self.assertEqual(rrf([['x'], ['y']], k=60), [('x', 1 / 61), ('y', 1 / 61)])  # ties break by id

    def test_rank_constant_changes_the_order(self):
        lists = [['d1', 'p', 'q', 'd2'], ['r', 's', 't', 'd2']]
        order = lambda k: [d for d, _ in rrf(lists, k=k)][:2]
        self.assertEqual(order(1), ['d1', 'r'])             # small k: a single first place wins (1/2 > 2/5)
        self.assertEqual(order(60)[0], 'd2')                # k = 60: agreement wins (2/64 > 1/61)
        with self.assertRaises(ValueError):
            rrf(lists, k=0)

    def test_invisible_chunks_never_retrieved_even_when_most_similar(self):
        k = 10
        for q in self.data['questions']:
            ids = set(self.index.bm25(q['question'], self.ctx, k)) | set(
                self.index.vector(q['vector'], self.model, self.ctx, k))
            self.assertFalse(ids & {'PM-044#1', 'RB-15#1', 'X-90#1', 'X-91#1'}, q['id'])
        security = dict(self.ctx, groups=['security'])
        self.assertIn('PM-044#1', self.index.vector(self.data['questions'][4]['vector'], self.model, security, k))

    def test_tenant_filter_holds_even_when_access_group_matches(self):
        x91 = self.index.chunks['X-91#1']
        self.assertTrue(set(x91.acl) & set(self.ctx['groups']))  # same group name, other tenant
        search_team = {'tenant': 'team-search', 'user': 'oncall-wu', 'groups': ['sre-all']}
        retrieved = lambda q, ctx: set(self.index.bm25(q['question'], ctx, 20)) | set(
            self.index.vector(q['vector'], self.model, ctx, 20, min_similarity=0))
        for q in self.data['questions']:
            self.assertIn('X-91#1', retrieved(q, search_team), q['id'])   # it matches every question
            self.assertNotIn('X-91#1', retrieved(q, self.ctx), q['id'])   # and never crosses the tenant

    def test_vector_query_must_use_the_index_embedding_model(self):
        qvec = self.data['questions'][1]['vector']
        with self.assertRaises(ValueError):
            self.index.vector(qvec, 'other-embed-v1', self.ctx, 3)      # same dimension, different model
        with self.assertRaises(ValueError):
            self.index.vector(qvec[:4], self.model, self.ctx, 3)         # dimension check is a minimum defence
        foreign = Chunk(**dict(self.data['chunks'][0], embedding_model='other-embed-v1'))
        with self.assertRaises(ValueError):
            Index([foreign], self.model)
        with self.assertRaises(ValueError):
            self.index.apply_change({'op': 'upsert', 'doc_id': 'RB-12', 'version': 3}, [foreign])

    def test_post_filtering_returns_fewer_than_k(self):
        qvec = [0.9, 0.4, 0.2, 0, 0, 0, 0, 0]
        pre = self.index.vector(qvec, self.model, self.ctx, 3, prefilter=True)
        post = self.index.vector(qvec, self.model, self.ctx, 3, prefilter=False)
        self.assertEqual(len(pre), 3)
        self.assertEqual(len(post), 2)                      # the draft RB-15#1 took the first slot
        self.assertTrue(all(visible(self.index.chunks[c], self.ctx) for c in pre + post))


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.data, self.index = load()

    def test_old_version_runbook_is_excluded_from_evidence(self):
        scope = {'service': 'payment-api', 'version': '1.8.3'}
        evidence, excluded, status = select_evidence(self.index, ['RB-11#1', 'RB-12#2'], scope)
        self.assertEqual((evidence, excluded, status), (['RB-12#2'], [('RB-11#1', 'version_mismatch')], 'answerable'))
        major_ten = {'service': 'payment-api', 'version': '10.2.0'}        # '10' must not match applies_to '1'
        self.assertEqual(select_evidence(self.index, ['RB-12#2'], major_ten),
                         ([], [('RB-12#2', 'version_mismatch')], 'insufficient_evidence'))

    def test_retrieved_but_inapplicable_material_means_insufficient_evidence(self):
        scope = {'service': 'ledger', 'version': '2.3.1'}
        evidence, excluded, status = select_evidence(self.index, ['RB-30#1'], scope)
        self.assertEqual(status, 'insufficient_evidence')
        self.assertEqual(excluded, [('RB-30#1', 'service_mismatch')])

    def test_no_evidence_for_this_user_is_not_no_evidence_at_all(self):
        q5 = self.data['questions'][4]
        model = self.data['settings']['embedding_model']
        security = dict(self.data['context'], groups=['security'])
        ids = self.index.vector(q5['vector'], model, security, 5)
        self.assertEqual(select_evidence(self.index, ids, q5['scope']), (['PM-044#1'], [], 'answerable'))

    def test_citation_checks_find_program_checkable_errors_only(self):
        ans = json.loads((HERE / 'answer_q3.json').read_text(encoding='utf-8'))
        issues = check_citations(ans, ans['context'], self.index)
        self.assertEqual(issues, [tuple(i) for i in ans['expected_program_issues']])
        flagged = {i for i, _ in issues}
        for i in ans['needs_semantic_review']:
            self.assertNotIn(i, flagged)                     # passes the program, still unsupported

    def test_numbers_match_as_whole_tokens(self):
        ctx = ['RB-12#2', 'PM-031#1']
        one = {'claims': [{'text': '观察 1 分钟', 'cites': [{'chunk': 'RB-12#2', 'quote': '观察 10 分钟内连接等待时间'}]}]}
        five = {'claims': [{'text': '上限改为 5', 'cites': [{'chunk': 'PM-031#1', 'quote': '把连接池上限从 50 改为 10'}]}]}
        ok = {'claims': [{'text': '上限从 50 改为 10', 'cites': [{'chunk': 'PM-031#1', 'quote': '把连接池上限从 50 改为 10'}]}]}
        self.assertEqual(check_citations(one, ctx, self.index), [(0, 'number_not_in_quote')])
        self.assertEqual(check_citations(five, ctx, self.index), [(0, 'number_not_in_quote')])
        self.assertEqual(check_citations(ok, ctx, self.index), [])

    def test_thousands_separators_are_normalised(self):
        chunk = Chunk(**dict(self.data['chunks'][0], id='T#1', doc_id='T',
                             text='上限从 1,000 调到 1000 以上，排队请求超过 500 时告警。'))
        index = Index([chunk], self.data['settings']['embedding_model'])
        cite = lambda claim, quote: {'claims': [{'text': claim, 'cites': [{'chunk': 'T#1', 'quote': quote}]}]}
        bad = cite('排队超过 1,500 时告警', '上限从 1,000 调到 1000 以上，排队请求超过 500')
        good = cite('上限为 1000', '上限从 1,000 调到')
        self.assertEqual(check_citations(bad, ['T#1'], index), [(0, 'number_not_in_quote')])
        self.assertEqual(check_citations(good, ['T#1'], index), [])

    def test_empty_or_tiny_quote_is_rejected(self):
        for quote in ('', '    ', '回滚'):            # four spaces: only strip() makes it short
            ans = {'claims': [{'text': '应回滚', 'cites': [{'chunk': 'RB-12#2', 'quote': quote}]}]}
            self.assertEqual(check_citations(ans, ['RB-12#2'], self.index), [(0, 'quote_too_short')], quote)

    def test_claim_without_citation_is_flagged(self):
        self.assertEqual(check_citations({'claims': [{'text': '直接重启'}]}, [], self.index), [(0, 'no_citation')])


class FreshnessAndMetricTests(unittest.TestCase):
    def setUp(self):
        self.data, self.index = load()
        self.ctx = self.data['context']

    def test_update_replaces_every_chunk_of_the_document(self):
        new = Chunk(**dict(self.data['chunks'][0], id='RB-12#1', doc_version=4,
                           text='适用于 payment-api 1.x。处置：只回滚连接池上限配置项。'))
        removed = self.index.apply_change({'op': 'upsert', 'doc_id': 'RB-12', 'version': 4}, [new])
        self.assertEqual(removed, 2)
        self.assertNotIn('RB-12#2', self.index.chunks)      # no orphan chunk from version 3
        self.assertEqual(self.index.stale_chunks(dict(self.data['source_versions'], **{'RB-12': 4})), [])

    def test_delete_removes_document_from_both_retrievers(self):
        q4 = self.data['questions'][3]
        self.index.apply_change({'op': 'delete', 'doc_id': 'PM-031'})
        self.assertNotIn('PM-031#1', self.index.bm25(q4['question'], self.ctx, 10))
        self.assertNotIn('PM-031#1', self.index.vector(q4['vector'], self.data['settings']['embedding_model'], self.ctx, 10))

    def test_stale_chunks_detect_index_lagging_behind_source(self):
        versions = dict(self.data['source_versions'], **{'RB-30': 3})
        del versions['PM-031']
        self.assertEqual(self.index.stale_chunks(versions), ['PM-031#1', 'RB-30#1', 'RB-30#2'])

    def test_metrics(self):
        self.assertEqual(recall_at_k(['a', 'b', 'c'], ['c', 'd'], 2), 0.0)
        self.assertEqual(recall_at_k(['a', 'b', 'c'], ['c', 'd'], 3), 0.5)
        self.assertEqual(reciprocal_rank(['a', 'b', 'c'], ['c'], 3), 1 / 3)
        self.assertEqual(reciprocal_rank(['a', 'b', 'c'], ['c'], 2), 0.0)      # outside the top k counts as missed
        with self.assertRaises(ValueError):
            recall_at_k(['a'], [], 1)                        # no-evidence questions are judged separately


if __name__ == '__main__':
    unittest.main()
