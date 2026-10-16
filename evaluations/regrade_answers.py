"""Rejudge completeness on saved conversations, without running the app or replacing originals.

python -m evaluations.regrade_answers RUN.json ... --output runs/answer-regrade --max-tokens 5000000
Paid judge calls. Tracing is disabled. Checkpoints permit resuming the exact same comparison.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextvars import copy_context
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

from evaluations.run_evidence import digest


def apply_verdict(attempt, verdict, quote):
    result=deepcopy(attempt)
    result['answered']=verdict
    result['answered_quote']=quote if verdict is False else None
    result['checks']=dict(result.get('checks',{}))
    result['ungraded']=[x for x in result.get('ungraded',[]) if x!='answers_every_part']
    if verdict is None:
        result['checks'].pop('answers_every_part',None)
        result['ungraded'].append('answers_every_part')
    else:
        result['checks']['answers_every_part']={'passed':verdict,'reason':quote if verdict is False else None}
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('records',type=Path,nargs='+')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--max-tokens',type=int,default=5000000)
    parser.add_argument('--workers',type=int,default=6)
    args=parser.parse_args(argv)
    if args.workers<1 or args.max_tokens<1:parser.error('workers and token allowance must be positive')
    os.environ['LANGFUSE_TRACING_ENABLED']='false'
    import evaluations.judge as judge, evaluations.evals as evals, todo.model_usage as model_usage
    from evaluations.eval_costs import estimate
    from evaluations.persona_report import save_record
    from todo.langfuse_setup import load_env
    load_env()
    sources=[(p,json.loads(p.read_text())) for p in args.records]
    if any(r.get('rejudged') for _,r in sources):raise ValueError('Use original run records, not a previous regrade.')
    original_digests=[digest(r) for _,r in sources]
    if len(set(original_digests))!=len(original_digests):raise ValueError('Duplicate source records.')
    root=Path(__file__).resolve().parents[1]
    settings={'sources':original_digests,'judge_model':judge.MODEL,'judge_settings':judge.SETTINGS,
              'source':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ('evaluations/judge.py','evaluations/evals.py','todo/model_usage.py','evaluations/regrade_answers.py')},
              'max_tokens':args.max_tokens,'workers':args.workers,
              'endpoint':digest(os.environ.get('OPENAI_BASE_URL','https://api.openai.com/v1'))}
    identity=digest(settings);out=args.output
    out.mkdir(parents=True,exist_ok=True)
    manifest=out/'manifest.json'
    if manifest.exists() and json.loads(manifest.read_text())['identity']!=identity:
        raise ValueError('Output belongs to a different comparison; use a new directory.')
    if not manifest.exists():save_record(manifest,{'identity':identity,'settings':settings,'created':datetime.now(timezone.utc).isoformat()})
    for n in settings['source']:
        (out/'source'/n).parent.mkdir(parents=True,exist_ok=True)
        (out/'source'/n).write_bytes((root/n).read_bytes())
    jobs=[];checkpoints={}
    for (_,r),source_digest in zip(sources,original_digests):
        for a in r['attempts']:
            key=digest([source_digest,a['case'],a['attempt']]);path=out/'attempts'/f'{key}.json'
            if path.exists():
                c=json.loads(path.read_text())
                if c['identity']!=identity or c['source_digest']!=source_digest:raise ValueError('Checkpoint mismatch.')
                checkpoints[key]=c
            else:jobs.append((key,path,source_digest,a))
    # Restore prior usage so resuming cannot reset the token allowance.
    with model_usage.capture(args.max_tokens) as shared:
        for c in checkpoints.values():shared.calls.extend(c['generations'])
        def task(key,path,source_digest,a):
            with model_usage.capture() as local:
                # Share the allowance across workers but keep this attempt's own evidence.
                original_check=local.check
                def check():
                    with shared.lock:shared.check()
                    original_check()
                local.check=check
                local.on_update=lambda summary: None
                verdict,quote=evals.every_turn_answered(a['conversation'],before=a['before'])
            with shared.lock:shared.calls.extend(local.calls)
            record={'identity':identity,'source_digest':source_digest,'case':a['case'],'attempt':a['attempt'],
                    'verdict':verdict,'quote':quote,'generations':local.calls}
            save_record(path,record)
            return key,record
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures=[pool.submit(task,*j) for j in jobs]
            for f in as_completed(futures):
                key,c=f.result();checkpoints[key]=c
                if len(checkpoints)%100==0:print('Checkpointed',len(checkpoints),'attempts',flush=True)
    for (p,r),source_digest in zip(sources,original_digests):
        result=deepcopy(r);calls=[]
        result['attempts']=[]
        for a in r['attempts']:
            c=checkpoints[digest([source_digest,a['case'],a['attempt']])]
            result['attempts'].append(apply_verdict(a,c['verdict'],c['quote']));calls.extend(c['generations'])
        result['rejudged']={'judge_commit':'source-'+settings['source']['evaluations/judge.py'][:12],
                            'judge_model':judge.MODEL,'check':'answers_every_part','source_record_digest':source_digest,
                            'comparison':identity,'created':datetime.now(timezone.utc).isoformat(),'cost_estimate':estimate(calls)}
        result['run']=r['run']+' [completeness rejudged]'
        save_record(out/(source_digest[:12]+'.json'),result)
        assert digest(json.loads(p.read_text()))==source_digest,'Original changed during comparison.'
    print('Saved separate rejudged records to',out,flush=True)


if __name__=='__main__':main()
