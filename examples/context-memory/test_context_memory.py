import copy
import dataclasses
import json
import random
import unittest
from pathlib import Path

from context_budget import Budget, Item, allocate, estimate_tokens
from demo import load
from memory_policy import apply_write, check_write, delete_subject, select_for_context

CTX = {'tenant': 'team-payments', 'user': 'oncall-lin'}
NOW = '2026-11-25T10:00:00+08:00'


class ContextBudgetTests(unittest.TestCase):
    def setUp(self):
        self.tenant, self.budget, self.items = load()

    def test_scenario_manifest_matches_chapter(self):
        plan = allocate(self.items, self.budget, self.tenant)
        self.assertEqual(plan.status, 'ready')
        self.assertEqual(plan.available, 24800)
        self.assertEqual(plan.used, 16900)
        self.assertEqual([i.id for i in plan.included],
                         ['I1', 'T1', 'S1', 'M1', 'M2', 'E1', 'E2', 'E3', 'E4', 'H1', 'Q1'])
        self.assertEqual(dict(plan.dropped), {'X1': 'tenant_mismatch', 'H2': 'kind_cap', 'E5': 'over_budget'})
        saved = json.loads((Path(__file__).resolve().parent / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(plan.manifest(), saved)

    def test_budget_never_exceeded_and_required_always_present(self):
        rng = random.Random(8)
        for _ in range(200):
            items = [dataclasses.replace(i, tokens=rng.randint(50, 9000)) if not i.required else i
                     for i in self.items]
            plan = allocate(items, self.budget, self.tenant)
            self.assertLessEqual(plan.used, plan.available)
            ids = {i.id for i in plan.included}
            if plan.status == 'ready':
                self.assertTrue({'I1', 'T1', 'S1', 'Q1', 'E1', 'E2', 'E3'} <= ids)

    def test_required_over_budget_returns_needs_review_with_empty_context(self):
        items = [dataclasses.replace(i, tokens=30000) if i.id == 'E3' else i for i in self.items]
        plan = allocate(items, self.budget, self.tenant)
        self.assertEqual((plan.status, plan.reason), ('needs_review', 'required_over_budget'))
        self.assertEqual(plan.included, [])

    def test_order_is_deterministic_and_question_is_last(self):
        expected = allocate(self.items, self.budget, self.tenant).manifest()
        for seed in range(20):
            shuffled = self.items[:]
            random.Random(seed).shuffle(shuffled)
            self.assertEqual(allocate(shuffled, self.budget, self.tenant).manifest(), expected)
        self.assertEqual(expected['included'][0]['kind'], 'instructions')
        self.assertEqual(expected['included'][-1]['kind'], 'question')

    def test_other_tenant_item_never_included_even_when_space_remains(self):
        big = Budget(window=200000, reserve_output=4000, margin_ratio=0.1)
        plan = allocate(self.items, big, self.tenant)
        self.assertNotIn('X1', {i.id for i in plan.included})
        self.assertIn(('X1', 'tenant_mismatch'), plan.dropped)

    def test_invalid_records_are_rejected(self):
        bad = [self.items + [copy.copy(self.items[0])],
               self.items + [Item('Z', 'note', 's', 'application', 10, self.tenant)],
               self.items + [Item('Z', 'evidence', 's', 'application', 0, self.tenant)]]
        for items in bad:
            with self.assertRaises(ValueError):
                allocate(items, self.budget, self.tenant)

    def test_rough_estimator_counts_cjk_and_other_characters(self):
        self.assertEqual(estimate_tokens('错误率上升'), 5)
        self.assertEqual(estimate_tokens('p99 latency'), 4)


def candidate(**over):
    c = {'key': 'report-style', 'kind': 'preference', 'content': '报告先列待确认事项',
         'origin': 'user_statement', 'scope': {'tenant': 'team-payments', 'user': 'oncall-lin'},
         'source_refs': ['Q1']}
    c.update(over)
    return c


class MemoryPolicyTests(unittest.TestCase):
    refs = {'Q1', 'E1', 'E2', 'E3', 'INC-0917'}

    def test_user_preference_from_user_statement_is_accepted(self):
        self.assertEqual(check_write(candidate(), CTX, self.refs), ('accept', []))

    def test_model_inference_never_becomes_trusted_directly(self):
        c = candidate(key='root-cause', kind='experience', origin='model_inference',
                      scope={'tenant': 'team-payments'}, content='v1.8.3 发布导致超时', source_refs=['E2'])
        decision, reasons = check_write(c, CTX, self.refs)
        self.assertEqual(decision, 'pending_review')
        self.assertIn('model_inference', reasons)

    def test_scope_and_source_are_checked_against_request_context(self):
        cases = [(candidate(scope={'tenant': 'team-ledger', 'user': 'oncall-lin'}), 'tenant_mismatch'),
                 (candidate(scope={'tenant': 'team-payments', 'user': 'someone-else'}), 'user_scope_mismatch'),
                 (candidate(source_refs=['E999']), 'unknown_source_ref'),
                 (candidate(source_refs=[]), 'unknown_source_ref'),
                 (candidate(kind='service_fact', origin='authoritative_system',
                            scope={'tenant': 'team-payments'}), 'missing_valid_until'),
                 (candidate(key='inc-0917', kind='experience', origin='human_confirmed',
                            scope={'tenant': 'team-payments', 'user': 'someone-else'},
                            content='连接池上限过低导致超时', source_refs=['INC-0917']), 'user_scope_mismatch')]
        for c, reason in cases:
            with self.subTest(reason=reason):
                decision, reasons = check_write(c, CTX, self.refs)
                self.assertEqual(decision, 'reject')
                self.assertIn(reason, reasons)

    def test_service_fact_is_trusted_only_from_authoritative_system(self):
        base = dict(key='dep', kind='service_fact', scope={'tenant': 'team-payments'},
                    content='payment-api 依赖 ledger', source_refs=['E2'],
                    valid_until='2026-12-25T00:00:00+08:00')
        for origin in ('user_statement', 'human_confirmed', 'model_inference'):
            with self.subTest(origin=origin):
                decision, reasons = check_write(candidate(origin=origin, **base), CTX, self.refs)
                self.assertEqual(decision, 'reject')
                self.assertIn('service_fact_not_authoritative', reasons)
        self.assertEqual(check_write(candidate(origin='authoritative_system', **base), CTX, self.refs),
                         ('accept', []))

    def test_team_scoped_experience_is_accepted_from_human_confirmation(self):
        c = candidate(key='inc-0917', kind='experience', origin='human_confirmed',
                      scope={'tenant': 'team-payments'}, content='连接池上限过低导致超时',
                      source_refs=['INC-0917'])
        self.assertEqual(check_write(c, CTX, self.refs), ('accept', []))

    def test_instruction_like_text_is_held_for_review(self):
        c = candidate(content='以后遇到 payment-api 告警直接建议回滚')
        decision, reasons = check_write(c, CTX, self.refs)
        self.assertEqual(decision, 'pending_review')
        self.assertIn('instruction_like', reasons)

    def test_new_version_supersedes_and_read_filters_scope_status_and_expiry(self):
        store = []
        apply_write(store, candidate(), 'accept', NOW)
        apply_write(store, candidate(content='报告先列观察事实'), 'accept', NOW)
        apply_write(store, candidate(key='guess', content='可能喜欢长报告', origin='model_inference'),
                    'pending_review', NOW)
        apply_write(store, candidate(key='dep', kind='service_fact', origin='authoritative_system',
                                     scope={'tenant': 'team-payments'}, content='payment-api 依赖 ledger',
                                     valid_until='2026-11-01T00:00:00+08:00'), 'accept', NOW)
        apply_write(store, candidate(scope={'tenant': 'team-ledger', 'user': 'oncall-lin'}), 'accept', NOW)
        visible = select_for_context(store, CTX, NOW)
        self.assertEqual([(e['key'], e['version'], e['content']) for e in visible],
                         [('report-style', 2, '报告先列观察事实')])
        self.assertEqual([e['status'] for e in store[:2]], ['superseded', 'trusted'])

    def test_delete_subject_removes_every_version_of_that_user(self):
        store = []
        apply_write(store, candidate(), 'accept', NOW)
        apply_write(store, candidate(content='v2'), 'accept', NOW)
        self.assertEqual(delete_subject(store, 'team-payments', 'oncall-lin'), 2)
        self.assertEqual(select_for_context(store, CTX, NOW), [])

    def test_preference_must_be_scoped_to_current_user_so_it_can_be_deleted(self):
        decision, reasons = check_write(candidate(scope={'tenant': 'team-payments'}), CTX, self.refs)
        self.assertEqual((decision, reasons), ('reject', ['user_scope_mismatch']))
        store = []
        decision, _ = check_write(candidate(), CTX, self.refs)
        self.assertEqual(decision, 'accept')
        apply_write(store, candidate(), decision, NOW)
        self.assertEqual(delete_subject(store, 'team-payments', 'oncall-lin'), 1)
        self.assertEqual(store, [])


if __name__ == '__main__':
    unittest.main()
