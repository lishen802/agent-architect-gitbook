"""Validate and summarize constructed teaching records, not judge natural language."""
import json
from pathlib import Path

CRITERIA = ('facts', 'scope', 'uncertainty', 'usefulness')


def contract_errors(output, case):
    """Small local report contract; not the complete chapter 5 Go validator."""
    errors = []
    if not isinstance(output, dict) or set(output) != {'assessment', 'findings', 'open_questions'}:
        return ['report_fields']
    if output['assessment'] not in ('draft', 'insufficient_data'):
        errors.append('assessment')
    questions = output['open_questions']
    if not isinstance(questions, list) or not all(isinstance(q, str) and q.strip() for q in questions):
        errors.append('questions')
    findings = output['findings']
    if not isinstance(findings, list):
        return errors + ['findings']
    known_ids = {e['id'] for e in case['evidence']}
    for finding in findings:
        if not isinstance(finding, dict) or set(finding) != {'kind', 'text', 'evidence_ids'}:
            errors.append('finding_fields')
            continue
        if finding['kind'] not in ('observation', 'hypothesis'):
            errors.append('kind')
        if not isinstance(finding['text'], str) or not finding['text'].strip():
            errors.append('text')
        ids = finding['evidence_ids']
        if not isinstance(ids, list) or not ids or not all(isinstance(i, str) and i in known_ids for i in ids):
            errors.append('evidence_ids')
    return sorted(set(errors))


def summarize(cases, runs):
    """This exercise requires exactly one record per planned case, including timeouts."""
    ids = [case['id'] for case in cases]
    run_ids = [run['case_id'] for run in runs]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('case IDs must be nonempty and unique')
    if len(run_ids) != len(set(run_ids)) or set(run_ids) != set(ids):
        raise ValueError('need exactly one record per case; missing/duplicate/unknown case')
    by_id = {run['case_id']: run for run in runs}
    counts = dict(planned=len(cases), completed=0, contract_pass=0, task_pass=0,
                  task_fail=0, task_pending=0)
    details = []
    for case in cases:
        run = by_id[case['id']]
        if run['origin'] != 'synthetic_teaching':
            raise ValueError('this example accepts teaching fixtures only')
        execution = run['execution']
        if execution not in ('completed', 'timeout', 'error'):
            raise ValueError('unknown execution state')
        reasons = []
        if execution != 'completed':
            if run['output'] is not None or run['review'] is not None:
                raise ValueError('failed execution must not contain a completed report or review')
            errors = None
            outcome = 'fail'
            reasons.append(execution)
        else:
            counts['completed'] += 1
            errors = contract_errors(run['output'], case)
            counts['contract_pass'] += int(not errors)
            reasons.extend(errors)
            if not errors and run['output']['assessment'] != case['expected_assessment']:
                reasons.append('assessment_mismatch')
            review = run['review']
            if review is None:
                pending = True
            else:
                if not isinstance(review, dict) or set(review) != set(CRITERIA):
                    raise ValueError('review must include all four criteria or be null')
                pending = False
                for key in CRITERIA:
                    item = review[key]
                    if item['verdict'] not in ('pass', 'fail', 'pending') or not isinstance(item['reason'], str) or not item['reason'].strip():
                        raise ValueError('each review criterion needs verdict and reason')
                    if item['verdict'] == 'fail':
                        reasons.append(key)
                    pending |= item['verdict'] == 'pending'
            # A known blocking failure remains a failure even if other review items are pending.
            outcome = 'fail' if reasons else ('pending' if pending else 'pass')
        counts['task_' + outcome] += 1
        details.append({'case_id': case['id'], 'contract': None if errors is None else not errors,
                        'outcome': outcome, 'reasons': reasons})
    return {'scope': 'synthetic_teaching_only', 'counts': counts, 'details': details}


def main():
    root = Path(__file__).resolve().parent
    result = summarize(json.loads((root / 'cases.json').read_text()),
                       json.loads((root / 'runs.json').read_text()))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
