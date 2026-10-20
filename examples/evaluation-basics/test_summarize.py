import copy
import json
from pathlib import Path
import unittest
from summarize import summarize

ROOT = Path(__file__).resolve().parent


class EvaluationAccountingTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads((ROOT / 'cases.json').read_text())
        self.runs = json.loads((ROOT / 'runs.json').read_text())

    def test_semantic_failure_and_timeout_stay_in_task_denominator(self):
        result = summarize(self.cases, self.runs)
        self.assertEqual(result['counts'], dict(planned=6, completed=5, contract_pass=5,
                                               task_pass=2, task_fail=4, task_pending=0))
        self.assertTrue(result['details'][0]['contract'])
        self.assertEqual(result['details'][0]['outcome'], 'fail')
        self.assertIn('timeout', result['details'][-1]['reasons'])

    def test_missing_duplicate_or_unknown_run_cannot_silently_change_population(self):
        variants = [self.runs[:-1], self.runs + [copy.deepcopy(self.runs[0])]]
        unknown = copy.deepcopy(self.runs)
        unknown[-1]['case_id'] = 'not-planned'
        variants.append(unknown)
        for runs in variants:
            with self.subTest(runs=len(runs)), self.assertRaises(ValueError):
                summarize(self.cases, runs)

    def test_missing_or_pending_review_never_becomes_pass(self):
        for review in (None, {'verdict': 'pending', 'reason': '待核对'}):
            runs = copy.deepcopy(self.runs)
            if review is None:
                runs[1]['review'] = None
            else:
                runs[1]['review']['facts'] = review
            result = summarize(self.cases, runs)
            self.assertEqual(result['details'][1]['outcome'], 'pending')
            self.assertEqual(result['counts']['task_pass'], 1)
            self.assertEqual(result['counts']['planned'], 6)

    def test_nonexistent_reference_blocks_even_with_all_positive_reviews(self):
        runs = copy.deepcopy(self.runs)
        runs[1]['output']['findings'][0]['evidence_ids'] = ['E999']
        result = summarize(self.cases, runs)
        self.assertFalse(result['details'][1]['contract'])
        self.assertEqual(result['details'][1]['outcome'], 'fail')

    def test_partial_review_is_a_record_error_not_implicit_pass(self):
        del self.runs[1]['review']['facts']
        with self.assertRaises(ValueError):
            summarize(self.cases, self.runs)


if __name__ == '__main__':
    unittest.main()
