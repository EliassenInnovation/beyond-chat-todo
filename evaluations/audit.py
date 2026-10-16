"""Read the evals, not just their scores: flag the conversations a person should read.

    .venv/bin/python -m evaluations.audit --digest runs/audit.md     # the newest full runs, as a readable digest

A green can hide a lenient check, and a red can be the eval's fault. From the last few full runs
this collects every failed or crashed conversation, how each case's pass count moved from run to
run (with the commit each run measured, when it was recorded), and a random sample of passing
conversations from the newest run. Each comes with an outline of what happened, so a reader can
classify it: a product bug, an eval bug, a judge bug, noise, or fine. No model is called.
"""

import argparse
import json
import random
from pathlib import Path

from evaluations.evals import RUNS, default_cases
from evaluations.eval_monitor import attempt_outcome


def full_runs(count):
    """The newest run records that ran every current case, newest last."""
    runs = []
    for path in sorted(RUNS.glob('2*.json')):
        record = json.loads(path.read_text())
        if {c['name'] for c in record.get('cases', [])} == set(default_cases()):
            runs.append((path, record))
    return runs[-count:]


def outline(attempt):
    """What was said and done, turn by turn, and what the list was after."""
    lines = []
    for turn in attempt['conversation']:
        if 'app' in turn:
            lines.append(f"- the person, in the app: {turn['app']}")
            continue
        lines.append(f"- user: {turn['user']}")
        for call in turn.get('tools', []):
            if call.get('given'):
                continue
            outcome = f"refused: {call['error']}" if 'error' in call else 'ok'
            lines.append(f"  - {call['tool']}({call.get('args') or ''}) → {outcome}")
        lines.append(f"- assistant: {turn.get('assistant', '(no reply)')}")
        if turn.get('list_after'):
            lines.append(f"  - list after: {state(turn['list_after'])}")
    lines.append(f"- saved at the end: {state(attempt['after'])}")
    return '\n'.join(lines)


def state(snapshot):
    if not snapshot:
        return '(not recorded)'
    todos = '; '.join(t['title'] + (' [done]' if t['done'] else '') + (f" (due {t['due']})" if t['due'] else '')
                      for t in snapshot['todos'])
    waiting = [p['title'] for p in snapshot.get('waiting_for_approval', [])]
    shown = snapshot.get('visible')
    return (todos or 'empty') + (f' | waiting for approval: {waiting}' if waiting else '') + \
        (f' | screen: {snapshot["screen_shows"]}, visible {shown}' if snapshot.get('screen_shows') not in (None, 'all') else '') + \
        (f' | highlighted: {snapshot["pointed_at"]}' if snapshot.get('pointed_at') else '')


def conversation(title, record, attempt):
    case = next(c for c in record['cases'] if c['name'] == attempt['case'])
    verdict = ('crashed: ' + attempt['error']) if attempt['error'] else \
        f"the case's check {'passed' if attempt['passed'] else 'not graded (a judge could not answer)' if attempt['passed'] is None else 'FAILED (the list, the screen, the highlight or the reply)'}, replies " + \
        {True: 'truthful', False: 'UNTRUTHFUL', None: 'not judged'}[attempt['truthful']]
    verdict += ', answers ' + {True: 'complete', False: 'INCOMPLETE', None: 'not judged'}[attempt.get('answered')]
    if attempt.get('ungraded'):
        verdict += '; missing checks: ' + ', '.join(attempt['ungraded'])
    return (f"### {title}: {attempt['case']}, attempt {attempt['attempt']}\n"
            f"Run {record['started'][:16]} (commit {record.get('commit', 'not recorded')}). {verdict}"
            + (f". Judge quoted: \"{attempt['judge_quote']}\"" if attempt['truthful'] is False else '') + '\n\n'
            f"Asks: {case.get('asks', 'Not recorded in this run.')}\nExpects: {case.get('expects', 'Not recorded in this run.')}\n"
            + (f"Trace: {attempt['trace_url']}\n" if attempt.get('trace_url') else '') + '\n'
            + outline(attempt) + '\n')


def digest(runs, greens, seed=0):
    newest_path, newest = runs[-1]
    parts = [f'# Evals audit digest\n\nFull runs read: {", ".join(r["started"][:16] for _, r in runs)}. '
             f'Newest: {newest_path.name}. This is a manual review across recorded revisions, not a statistical-control assessment.\n']
    # How each case moved: a case that passes in one run and fails in the next is read, not assumed noise.
    parts.append('## Pass counts per case, oldest run first\n')
    for name in (c['name'] for c in newest['cases']):
        counts = []
        for _, record in runs:
            attempts = [a for a in record['attempts'] if a['case'] == name]
            counts.append(f"{sum(attempt_outcome(a) == 'passed' for a in attempts)}/{record.get('repeat', len(attempts))}")
        moved = len(set(counts)) > 1
        parts.append(f"- {name}: {' '.join(counts)}{'   ← moved' if moved else ''}")
    parts.append('\n## Every failed or crashed conversation\n')
    failed = [(record, a) for _, record in runs for a in record['attempts']
              if attempt_outcome(a) == 'failed']
    parts += [conversation('Failed', record, a) for record, a in failed] or ['None.\n']
    parts.append('\n## Inconclusive conversations (missing judgments)\n')
    incomplete = [(r,a) for _,r in runs for a in r['attempts'] if attempt_outcome(a) == 'inconclusive']
    parts += [conversation('Inconclusive', r, a) for r,a in incomplete] or ['None.\n']
    parts.append(f'\n## Passing conversations, a random {greens} per case from the newest run\n')
    rng = random.Random(seed)
    for name in (c['name'] for c in newest['cases']):
        good = [a for a in newest['attempts'] if a['case'] == name and attempt_outcome(a) == 'passed']
        parts += [conversation('Passed', newest, a) for a in rng.sample(good, min(greens, len(good)))]
    return '\n'.join(parts), len(failed)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--digest', default=str(RUNS / 'audit.md'))
    parser.add_argument('--runs', type=int, default=5, help='how many recent full runs to read')
    parser.add_argument('--greens', type=int, default=1, help='passing conversations sampled per case')
    args = parser.parse_args(argv)
    if args.runs < 1 or args.greens < 0:
        parser.error('--runs must be positive and --greens nonnegative')
    runs = full_runs(args.runs)
    if not runs:
        raise SystemExit('No full run yet: run evals.py first.')
    text, failed = digest(runs, args.greens)
    Path(args.digest).write_text(text)
    print(f'{args.digest}: {len(runs)} runs, {failed} failed conversations, '
          f'{args.greens} passing per case sampled.')


if __name__ == '__main__':
    main()
