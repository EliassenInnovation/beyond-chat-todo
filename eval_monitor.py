"""Frozen control baselines and acceptance checks, independent of model graders and Langfuse.

Freeze only reviewed, comparable runs:
    python eval_monitor.py freeze --output runs/control-baseline.json RUN1.json ... RUN20.json

Twenty reviewed runs is a starting requirement for this sample, not proof of statistical control.
"""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import statistics

from run_evidence import digest

MIN_BASELINE_RUNS = 20


def attempt_outcome(attempt):
    if attempt.get('error') or any(attempt.get(k) is False for k in ('passed', 'truthful', 'answered')):
        return 'failed'
    if not attempt.get('ungraded') and all(attempt.get(k) is True for k in ('passed', 'truthful', 'answered')):
        return 'passed'
    return 'inconclusive'


def counts(record):
    expected = {(c['name'], n) for c in record['cases'] for n in range(1, record['repeat'] + 1)}
    attempts = record['attempts']
    observed = [(a['case'], a['attempt']) for a in attempts]
    missing = len(expected - set(observed))
    invalid = len(observed) != len(set(observed)) or bool(set(observed) - expected)
    passed = sum(attempt_outcome(a) == 'passed' for a in attempts)
    failed = sum(attempt_outcome(a) == 'failed' for a in attempts)
    ungraded = sum(any(a.get(k) is None for k in ('passed', 'truthful', 'answered'))
                   or bool(a.get('ungraded')) for a in attempts)
    missing_outcomes = sum(a.get('after') is None for a in attempts)
    complete = not (missing or invalid or ungraded or missing_outcomes) and bool(expected)
    return dict(expected=len(expected), passed=passed, failed=failed, missing=missing,
                ungraded=ungraded, missing_outcomes=missing_outcomes, invalid=invalid, complete=complete,
                failure_rate=failed / len(expected) if complete else None)


def comparison_key(record):
    config = record.get('configuration') or {}
    if not config.get('fingerprint') or digest(config.get('settings')) != config['fingerprint']:
        return None
    generations = record.get('generations') or []
    successful = [g for g in generations if not g.get('error')]
    if record.get('rejudged'):
        return None
    if not successful or any(not g.get('served_model') for g in successful):
        return None
    served = sorted({(g['purpose'], g['served_model']) for g in successful})
    if not any(purpose == 'agent' for purpose, _ in served) or not any(purpose.startswith('judge') for purpose, _ in served):
        return None
    return digest({'configuration': config['fingerprint'], 'served': served,
                   'provider_metadata': sorted({(g['purpose'], g.get('service_tier') or 'not reported',
                                                g.get('system_fingerprint') or 'not reported') for g in successful})})


def signal(values, center, lower, upper):
    """Predeclared rules: beyond three-sigma limits or eight strictly on one side."""
    latest = values[-1]
    if latest > upper:
        return 'Higher failure rate beyond the upper control limit.'
    if latest < lower:
        return 'Lower failure rate beyond the lower control limit; investigate improvement too.'
    if len(values) >= 8:
        last = values[-8:]
        if all(v > center for v in last):
            return 'Eight consecutive runs above the baseline average failure rate.'
        if all(v < center for v in last):
            return 'Eight consecutive runs below the baseline average failure rate.'
    return None


def freeze(records):
    if len(records) < MIN_BASELINE_RUNS:
        raise ValueError(f'Choose at least {MIN_BASELINE_RUNS} reviewed runs; fewer cannot establish this baseline.')
    records = sorted(records, key=lambda r: r['started'])
    ids = [r['run'] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError('A run may appear only once in a baseline.')
    key = comparison_key(records[0])
    if key is None or any(comparison_key(r) != key for r in records):
        raise ValueError('Baseline runs need matching recorded configurations and reported served models.')
    if any(not counts(r)['complete'] for r in records):
        raise ValueError('Baseline runs must have every planned attempt and every required judgment and saved outcome.')
    settings = records[0]['configuration']['settings']
    if settings.get('inject') or settings.get('shuffled'):
        raise ValueError('Fault-injected and shuffled-tool experiments are not normal-operation baselines.')
    values = [counts(r)['failure_rate'] for r in records]
    center = statistics.mean(values)
    moving_range = statistics.mean(abs(b - a) for a, b in zip(values, values[1:]))
    if moving_range == 0:
        raise ValueError('No observed variation: control limits cannot be estimated from these runs.')
    lower, upper = center - 2.66 * moving_range, center + 2.66 * moving_range
    for i in range(len(values)):
        if signal(values[:i + 1], center, lower, upper):
            raise ValueError('The proposed baseline contains a signal. Investigate before freezing it; do not silently discard runs.')
    baseline = dict(version=1, method='individuals-moving-range', minimum_runs=MIN_BASELINE_RUNS,
                    created=datetime.now(timezone.utc).isoformat(), comparison_key=key,
                    center=center, lower=lower, upper=upper, moving_range=moving_range,
                    rules=['one beyond limits', 'eight on one side'],
                    runs=[dict(run=r['run'], started=r['started'], failure_rate=v, record_digest=digest(r))
                          for r, v in zip(records, values)])
    baseline['baseline_digest'] = digest(baseline)
    return baseline


def valid_baseline(baseline):
    if not isinstance(baseline, dict) or baseline.get('version') != 1:
        return False
    if baseline.get('baseline_digest') != digest({k: v for k, v in baseline.items() if k != 'baseline_digest'}):
        return False
    if baseline.get('method') != 'individuals-moving-range' or not baseline.get('comparison_key'):
        return False
    if any(not isinstance(baseline.get(k), (int, float)) or not math.isfinite(baseline[k])
           for k in ('center', 'lower', 'upper', 'moving_range')):
        return False
    rows = baseline.get('runs')
    if not isinstance(rows, list) or len(rows) < MIN_BASELINE_RUNS:
        return False
    if any(not isinstance(r, dict) or not {'run','started','record_digest','failure_rate'} <= r.keys() for r in rows):
        return False
    return (0 <= baseline['center'] <= 1 and baseline['moving_range'] > 0
            and baseline['lower'] < baseline['center'] < baseline['upper']
            and len({r['run'] for r in rows}) == len(rows))


def stability(record, baseline=None, history=()):
    current = counts(record)
    if not current['complete']:
        return dict(status='incomplete', message='Incomplete evidence: resolve missing attempts or judgments before assessing variation.')
    if baseline is None:
        return dict(status='baseline_needed', message='No reviewed control baseline. A single run cannot establish statistical control.')
    if not valid_baseline(baseline):
        return dict(status='invalid_baseline', message='Baseline is invalid or was edited; rebuild it from its reviewed run records.')
    key = comparison_key(record)
    if key is None or key != baseline['comparison_key']:
        return dict(status='not_comparable', message='Configuration or served models differ, or evidence is missing. Treat this as a new phase, not common-cause variation against this baseline.')
    member = next((r for r in baseline['runs'] if r['run'] == record['run']), None)
    if member and member['record_digest'] != digest(record):
        return dict(status='changed_record', message='This baseline run record was changed after the baseline was frozen.')
    if member:
        return dict(status='baseline_member', message='This run helped estimate the limits; it is not an independent check against them.')
    last = baseline['runs'][-1]
    if record['started'] <= last['started']:
        return dict(status='not_comparable', message='The evaluated run must follow the frozen baseline.')
    # An incompatible or incomplete intervening run breaks a sequence. Do not cherry-pick
    # comparable points across interruptions to manufacture an eight-run signal.
    recent = sorted([r for r in history if last['started'] < r['started'] < record['started']], key=lambda r: r['started'])
    values = [r['failure_rate'] for r in baseline['runs']]
    seen = set()
    for r in recent:
        if r['run'] in seen:
            return dict(status='invalid_history', message='Duplicate run records make this history ambiguous.')
        seen.add(r['run'])
        if comparison_key(r) != key or not counts(r)['complete']:
            values = []
        else:
            values.append(counts(r)['failure_rate'])
    values.append(current['failure_rate'])
    reason = signal(values, baseline['center'], baseline['lower'], baseline['upper'])
    return dict(status='signal' if reason else 'no_signal',
                message=reason or 'No signal under the chosen rules. This does not establish acceptable performance.',
                failure_rate=current['failure_rate'], center=baseline['center'],
                lower=baseline['lower'], upper=baseline['upper'], baseline_runs=len(baseline['runs']))


def acceptance(record, policy=None):
    """Product thresholds are explicit decisions, not estimated from control limits."""
    policy = policy or {}
    threshold = policy.get('minimum_pass_rate')
    checks = policy.get('concern_checks', [])
    known = {'passed', 'claims_match_outcome', 'claims_real_abilities', 'claims_real_approvals', 'receipts_repeated', 'answers_every_part'}
    if not isinstance(checks, list) or any(not isinstance(c, str) or c not in known for c in checks):
        raise ValueError('concern_checks must list existing check names.')
    if threshold is not None and (isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1):
        raise ValueError('minimum_pass_rate must be null or a number between 0 and 1.')
    flagged = [dict(case=a['case'], attempt=a['attempt'], check=name)
               for a in record['attempts'] for name in checks
               if a.get('checks', {}).get(name, {}).get('passed') is False]
    if flagged:
        return dict(status='concern', message='A designated check failed; review it regardless of statistical stability.', flagged=flagged)
    if not counts(record)['complete']:
        return dict(status='inconclusive', message='Required evidence is missing; acceptance cannot be established.')
    if threshold is None:
        return dict(status='not_configured', message='No minimum acceptable pass rate has been chosen.')
    rate = counts(record)['passed'] / counts(record)['expected']
    return dict(status='meets_target' if rate >= threshold else 'below_target',
                message=f'Observed pass rate {rate:.1%}; required {threshold:.1%}. This is a run-level decision, not a guarantee of the true rate.')


def read_runs(folder):
    result = []
    for path in Path(folder).glob('*.json'):
        try:
            record = json.loads(path.read_text())
            if isinstance(record, dict) and {'attempts', 'cases', 'repeat', 'run', 'started'} <= record.keys():
                result.append(record)
        except (OSError, ValueError):
            continue
    return sorted(result, key=lambda r: r['started'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    create = sub.add_parser('freeze', help='freeze reviewed comparable runs; refuses to overwrite a baseline')
    create.add_argument('--output', type=Path, required=True)
    create.add_argument('runs', type=Path, nargs='+')
    args = parser.parse_args(argv)
    try:
        baseline = freeze([json.loads(p.read_text()) for p in args.runs])
        with args.output.open('x') as out:
            json.dump(baseline, out, indent=2)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(args.output)


if __name__ == '__main__':
    main()
