"""Do the judges agree with a person? Replay labelled replies through them and count.

    .venv/bin/python judge_calibration.py                    # every question, 3 judgements per case
    .venv/bin/python judge_calibration.py --question asks --vote

Each question has its file of real replies a person read and labelled, with why:
  claims    judge_cases.json    does a reply claim a change its turn's saved list does not show?
  asks      ask_cases.json      does a reply ask the user before making the change?
  abilities feature_cases.json  does a reply claim, offer or accept an ability the app lacks?
  approvals approval_cases.json does a reply claim or ask for an approval that is not waiting?
  answers   answer_cases.json   does a reply leave a request or question in the message without a response?
(Silence when asked for a missing ability is checked in code, evals.silent_on_request; test_main.py.)
--vote judges each case by majority (ask twice, a third time on a split). Measured on the claims
set it did not help (106/115 against 107/115 single: the errors are the same every time), so the
evals ask once; the option stays for measuring a judge that looks noisy.
Run this after any change to a judge's question: a false alarm fails a good answer, a miss passes a bad one.

The labels were written by the coding agent, one by one against the saved list; a person samples them.
label_checks.json records each label a person read and whether they agreed, and every calibration says how
many were checked and how many changed, so a score against labels a model wrote is not taken for more than
it is (review 2026-10-03, item 5). --sample N prints N labels nobody has checked yet, for a person to read.
"""

import argparse
import json
import random
from pathlib import Path

from judge import answers_every_part, asks_first, claims_match_outcome, claims_real_abilities, claims_real_approvals, vote
from langfuse_setup import connect

HERE = Path(__file__).parent
QUESTIONS = {
    # name: (cases file, the label that means "the judge should say True", one judgement of a case)
    'claims': (HERE / 'judge_cases.json', 'truthful',
               lambda c: claims_match_outcome(c['conversation'], c['before'], c['conversation'][-1]['list_after'])),
    'asks': (HERE / 'ask_cases.json', 'asks', lambda c: asks_first(c['user'], c['reply'])),
    'abilities': (HERE / 'feature_cases.json', 'truthful', lambda c: claims_real_abilities(c['conversation'])),
    'approvals': (HERE / 'approval_cases.json', 'truthful', lambda c: claims_real_approvals(c['conversation'])),
    'answers': (HERE / 'answer_cases.json', 'answered', lambda c: answers_every_part(c['user'], c['reply'])),
}
CASES = QUESTIONS['claims'][0]  # kept for the test of the claims file
CHECKS = HERE / 'label_checks.json'  # [{"set", "name", "by", "on", "agreed", "note"}], one per label a person read


def checks(name, path=None):
    """(checked, changed, labelled): how many of this set's labels a person read, how many they disagreed with."""
    done = [c for c in json.loads((path or CHECKS).read_text()) if c['set'] == name] if (path or CHECKS).exists() else []
    labelled = len(json.loads(QUESTIONS[name][0].read_text()))
    return len({c['name'] for c in done}), sum(not c['agreed'] for c in done), labelled


def sample(name, n, rng=random):
    """n labels in this set that no person has checked, to read against their evidence."""
    checked = {c['name'] for c in json.loads(CHECKS.read_text()) if c['set'] == name} if CHECKS.exists() else set()
    open_ = [c for c in json.loads(QUESTIONS[name][0].read_text()) if c['name'] not in checked]
    for case in rng.sample(open_, min(n, len(open_))):
        print(f"\n[{name}] {case['name']}: labelled {case['expect']} ({case['why']})")
        print(json.dumps({k: v for k, v in case.items() if k not in ('name', 'expect', 'why')}, indent=1, ensure_ascii=False))


def calibrate(name, repeat, voted):
    path, positive, judge = QUESTIONS[name]
    agree = total = false_alarms = misses = 0
    for case in json.loads(path.read_text()):
        want = case['expect'] == positive
        verdicts = [(vote(lambda: judge(case)) if voted else judge(case))[0] for _ in range(repeat)]
        right = sum(v == want for v in verdicts)
        agree, total = agree + right, total + len(verdicts)
        false_alarms += sum(v is False for v in verdicts) if want else 0
        misses += sum(v is True for v in verdicts) if not want else 0
        if right < len(verdicts):
            print(f"  {right}/{len(verdicts)}  {case['name']}: {'false alarm' if want else 'missed'}. {case['why']}")
    checked, changed, labelled = checks(name)
    print(f'{name}{" (voted)" if voted else ""}: agrees {agree}/{total}, '
          f'false alarms {false_alarms}, misses {misses}. Labels checked by a person: {checked} of {labelled}, '
          f'{changed} changed')


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--question', choices=sorted(QUESTIONS), action='append', help='default: all')
    parser.add_argument('--repeat', type=int, default=3)
    parser.add_argument('--vote', action='store_true', help='judge each case by majority')
    parser.add_argument('--sample', type=int, metavar='N', help='print N labels no person has checked, and stop')
    args = parser.parse_args(argv)
    if args.sample:
        for name in args.question or list(QUESTIONS):
            sample(name, args.sample)
        return
    langfuse, _ = connect()
    try:
        for name in args.question or list(QUESTIONS):
            calibrate(name, args.repeat, args.vote)
    finally:
        langfuse.flush()


if __name__ == '__main__':
    main()
