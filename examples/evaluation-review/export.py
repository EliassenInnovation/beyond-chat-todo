"""Recreate this curated example from the original local synthetic collection.

python examples/evaluation-review/export.py runs/guarded-baseline-2026-10-15
For an ordinary checkout, regenerate HTML from collection.json using eval_collection.py.
"""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import evaluations.eval_monitor as eval_monitor
from evaluations.eval_costs import estimate
from evaluations.run_evidence import digest
from evaluations.eval_collection import render

SELECTION = [
 ('run-08','no-email',2,'Responding to an email request','Did this reply address the email request, even though the app cannot send email?', 'The reply explicitly declines email and supplies the list. Completeness and task completion are different checks.'),
 ('run-01','put-it-back',2,'Restoring a change after undo','Does the final reply address the request when read in context?', 'The merge is restored after undo. The old completeness judge did not receive earlier turns.'),
 ('run-06','merge-which-two',2,'Clarifying which tasks to merge','Does the assistant ask which tasks without changing them?', 'The reply asks which two items. The recorded clarification judgment was negative.'),
 ('run-04','overdue-first',3,'Overdue tasks and completed tasks','Does the reply accurately describe the current state and overdue work?', 'The filtered view and stored completion state support the reply. The old claim grader flagged the already-done statement.'),
 ('run-05','no-email',3,'Adding a task after an email request','Is creating an email task an appropriate substitute for the requested email?', 'The assistant adds a task despite receiving no request to add one. The limitation disclosure does not undo that action.'),
 ('run-06','which-call-v2',2,'Assigning a date to a call','Did the user identify which call should receive the date?', 'The app has multiple calls; the assistant changes one without clarification. The merge-specific guard does not cover date changes.'),
 ('run-01','overdue-first',3,'Deletion and overdue work','Did the reply turn to the overdue work as well as the deletion request?', 'It handles deletion but does not turn to the overdue tasks. This is a meaningful completeness concern, not merely preferred wording.'),
 ('run-19','back-there',2,'Returning a task to its previous position','Did the task return to its original position?', 'The task started third and ended second. A fluent receipt accurately describes the wrong action.'),
]


def export(folder):
    records={}
    for p in folder.glob('run-*/*.json'):
        r=json.loads(p.read_text())
        if 'attempts' in r and 'configuration' in r:
            if p.parent.name in records: raise ValueError('More than one record in a run folder.')
            if r.get('tracing_enabled') or any(a.get('trace_url') for a in r['attempts']):
                raise ValueError('This curated example requires local records without trace links.')
            if any(c.get('origin')=='held out' for c in r['cases']):
                raise ValueError('Do not publish held-out cases in this example.')
            records[p.parent.name]=r
    ordered=sorted(records.items(),key=lambda pair:pair[1]['started'])
    observations=[]
    for name,r in ordered:
        c=eval_monitor.counts(r)
        observations.append(dict(run=r['run'],run_label=name,started=r['started'],source_digest=digest(r),configuration=r['configuration']['fingerprint'],comparison_key=eval_monitor.comparison_key(r),expected=c['expected'],passed=c['passed'],failed=c['failed'],inconclusive=c['expected']-c['passed']-c['failed'],complete=c['complete'],cost_usd=estimate(r['generations'])['usd']))
    candidate=eval_monitor.freeze([r for _,r in ordered])
    examples=[]
    for run,case,number,title,question,note in SELECTION:
        r=records[run];a=next(a for a in r['attempts'] if a['case']==case and a['attempt']==number)
        examples.append(dict(id=f'{run}:{case}:{number}',run=r['run'],run_label=run,source_digest=digest(r),title=title,question=question,assistant_note=note,expectation=next(c['expects'] for c in r['cases'] if c['name']==case),attempt={k:a[k] for k in ('case','attempt','passed','truthful','answered','checks','conversation','before','after')}))
    bundle=dict(version=1,title='Reading the todo app’s evaluations',observations=observations,examples=examples,candidate_limits={k:candidate[k] for k in ('center','lower','upper','moving_range')},conclusion='All 20 runs have complete evidence, and no declared chart signal appeared. Review found real application errors mixed with apparent grader false alarms. These results do not yet establish an accepted baseline of application quality.',chart_note='Dashed lines are calculated from these same 20 observations, not independent validation. No point exceeds a limit and no eight consecutive points lie strictly on one side. Back-to-back, partly concurrent runs mainly describe short-term variation. Points are ordered by start time, not run number or elapsed time.',provenance='Collected October 15, 2026 with GPT-6 Luna for the assistant, judges and restored merge guard; 51 visible synthetic cases × 3 attempts × 20 runs. Original grades retained. The later contextual completeness grader was not used for this collection. Examples were selected to illustrate review decisions, not estimate grader accuracy. No real user conversations, trace links or provider credentials are included.')
    bundle['bundle_digest']=digest(bundle)
    return bundle


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('collection',type=Path);args=parser.parse_args()
    bundle=export(args.collection);here=Path(__file__).resolve().parent
    (here/'collection.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
    (here/'index.html').write_text(render(bundle))
