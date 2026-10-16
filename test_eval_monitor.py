from copy import deepcopy
import json

import pytest
from eval_monitor import acceptance, comparison_key, counts, freeze, read_runs, signal, stability
from run_evidence import digest
from eval_costs import estimate


def record(number, failures=10):
    settings = {'cases': ['job'], 'repeat': 100, 'source': {'agent.py': 'unchanged'}, 'inject': 0, 'shuffled': False}
    return dict(run=f'run-{number}', started=f'2026-10-{number:02}T12:00:00Z', cases=[{'name':'job'}], repeat=100,
                attempts=[dict(case='job', attempt=n, passed=n>failures, truthful=True, answered=True,
                               after={}, ungraded=[], checks={'passed': {'passed': n>failures}}) for n in range(1,101)],
                configuration={'settings':settings,'fingerprint':digest(settings)},
                generations=[{'purpose':'agent','served_model':'model-v1'}, {'purpose':'judge-claims','served_model':'model-v1'}])


def baseline_records():
    return [record(i+1, failures=[10,12,8,10][i%4]) for i in range(20)]


def test_complete_means_all_attempts_judgments_and_outcomes():
    r=record(1); assert counts(r)['complete']
    r['attempts'][0]['truthful']=None
    assert not counts(r)['complete'] and counts(r)['failed']==10  # known failure remains a failure
    r=record(1);r['attempts'][0]['after']=None
    assert counts(r)['missing_outcomes']==1 and not counts(r)['complete']
    r=record(1);r['attempts'].pop()
    assert counts(r)['missing']==1
    r['attempts'].append(deepcopy(r['attempts'][0]))
    assert counts(r)['invalid'] and counts(r)['missing']==1
    assert counts(r)['failure_rate'] is None


def test_inconsistent_ungraded_flag_cannot_be_a_pass():
    r=record(1,0);r['attempts'][0]['ungraded']=['claims_real_abilities']
    assert counts(r)['passed']==99 and not counts(r)['complete']


def test_config_and_served_models_define_comparability():
    r=record(1);original=comparison_key(r)
    r['generations'][0]['served_model']='model-v2'
    assert comparison_key(r)!=original
    r['configuration']['settings']['source']['agent.py']='changed'
    assert comparison_key(r) is None
    r=record(1);r['generations'][0]['served_model']=None
    assert comparison_key(r) is None
    r=record(1);r['rejudged']={'judge_model':'new'}
    assert comparison_key(r) is None


def test_regraded_report_separates_evidence_comparability_and_cost():
    from evals_page import render
    r = record(1)
    r['model'] = 'example'
    r['cases'][0].update(asks='Does it work?', expects='the expected state')
    for attempt in r['attempts']:
        attempt.update(error=None, trace_url=None, conversation=[], judge_quote=None, answered_quote=None)
    r['rejudged'] = dict(judge_commit='source-123', judge_model='new',
                         check='answers_every_part', cost_estimate={'usd': .1234})
    page = render(r)
    assert '<h2>Complete</h2>' in page
    assert 'Saved replies judged again' in page
    assert 'excluded from control-chart comparisons' in page
    assert 'Additional estimated judge cost: $0.1234' in page
    assert 'Estimated original run API cost:' in page
    r['attempts'][0]['answered'] = None
    assert '<h2>Incomplete</h2>' in render(r)


def test_baseline_requires_enough_comparable_reviewed_variation():
    with pytest.raises(ValueError,match='at least 20'): freeze(baseline_records()[:5])
    with pytest.raises(ValueError,match='No observed variation'): freeze([record(i) for i in range(1,21)])
    rows=baseline_records();rows[-1]=rows[0]
    with pytest.raises(ValueError,match='once'): freeze(rows)
    rows=baseline_records();rows[-1]['attempts'].pop()
    with pytest.raises(ValueError,match='every planned'): freeze(rows)
    rows=baseline_records();rows[-1]['generations'][0]['served_model']='different'
    with pytest.raises(ValueError,match='matching'): freeze(rows)


def test_stable_does_not_mean_acceptable_and_signal_is_separate():
    baseline=freeze(baseline_records())
    assert stability(record(21),baseline)['status']=='no_signal'
    assert acceptance(record(21), {'minimum_pass_rate':.95})['status']=='below_target'
    assert stability(record(21,30),baseline)['status']=='signal'
    assert stability(record(21))['status']=='baseline_needed'
    assert acceptance(record(21))['status']=='not_configured'


def test_designated_failure_matters_even_when_other_evidence_missing():
    r=record(21);r['attempts'][-1]['answered']=None
    assert acceptance(r,{'concern_checks':['passed']})['status']=='concern'
    assert acceptance(r,{'minimum_pass_rate':.8})['status']=='inconclusive'
    with pytest.raises(ValueError): acceptance(r,{'concern_checks':['typo']})
    with pytest.raises(ValueError): acceptance(r,{'minimum_pass_rate':float('nan')})


def test_frozen_baseline_is_not_reestimated_from_new_bad_run():
    baseline=freeze(baseline_records());before=deepcopy(baseline)
    stability(record(21,50),baseline)
    assert baseline==before
    baseline['center']=.5
    assert stability(record(21),baseline)['status']=='invalid_baseline'


def test_eight_point_rule_and_missing_run_breaks_sequence():
    baseline=freeze(baseline_records())
    history=[record(i,12) for i in range(21,28)]
    assert stability(record(28,12),baseline,history)['status']=='signal'
    history[3]['attempts'].pop()
    assert stability(record(28,12),baseline,history)['status']=='no_signal'
    assert signal([.1]*8,.1,0,.2) is None  # ties are not above or below


def test_auxiliary_and_persona_records_do_not_become_latest_eval(tmp_path):
    (tmp_path/'run.json').write_text(json.dumps(record(1)))
    (tmp_path/'budget.json').write_text(json.dumps({'calls':99}))
    (tmp_path/'personas.json').write_text('[]')
    (tmp_path/'broken.json').write_text('{')
    assert [r['run'] for r in read_runs(tmp_path)]==['run-1']


def test_cost_uses_cached_subset_once_and_never_guesses_unknown_models():
    rows=[{'served_model':'gpt-6-luna', 'usage':{'prompt_tokens':1000000,'completion_tokens':1000,
           'prompt_tokens_details':{'cached_tokens':800000}}}]
    # Long context is deliberately unpriced in this sample.
    assert estimate(rows)['usd'] is None
    rows[0]['usage']['prompt_tokens']=100000
    rows[0]['usage']['prompt_tokens_details']['cached_tokens']=80000
    assert estimate(rows)['usd']==pytest.approx(.0033)
    rows.append({'served_model':'unknown','usage':{}})
    assert estimate(rows)['usd'] is None and estimate(rows)['known_usd']==pytest.approx(.0033)


def test_context_reaches_async_worker_and_metadata_contains_no_prompt():
    import asyncio
    from types import SimpleNamespace
    from model_usage import capture, attempt, call_model
    async def one(name):
        with attempt(name,1):
            return await asyncio.to_thread(call_model,lambda **kwargs: SimpleNamespace(model='served',usage=None),
                                           purpose='agent', model='requested', messages=['private text'])
    with capture() as usage:
        async def both(): await asyncio.gather(one('a'),one('b'))
        asyncio.run(both())
    assert {row['case'] for row in usage.calls}=={'a','b'}
    assert 'private text' not in json.dumps(usage.summary())


def test_eval_runner_saves_raw_attempt_before_grading_and_complete_record_after(monkeypatch, tmp_path):
    import asyncio
    from types import SimpleNamespace
    import evals
    monkeypatch.setattr(evals, 'RUNS', tmp_path)
    monkeypatch.setattr(evals, 'commit', lambda: 'test-revision')
    monkeypatch.setattr(evals, 'play', lambda case: dict(before={}, after={}, conversation=[], served=[], duration_seconds=0))
    monkeypatch.setattr(evals, 'grade', lambda *a: True)
    monkeypatch.setattr(evals, 'claims_match_outcome', lambda *a: (True, ''))
    monkeypatch.setattr(evals, 'claims_real_abilities', lambda *a: (True, ''))
    monkeypatch.setattr(evals, 'claims_real_approvals', lambda *a: (True, ''))
    monkeypatch.setattr(evals, 'report', lambda *a: None)
    monkeypatch.setattr(evals, 'refresh_page', lambda *a, **kw: None)
    def experiment(**kwargs):
        item=kwargs['data'][0]
        output=asyncio.run(kwargs['task'](item=item))
        partial=list((tmp_path/'partial').rglob('*.json'))
        assert len(partial)==1
        assert json.loads(partial[0].read_text())['graded'] is False
        scores=[]
        for evaluator in kwargs['evaluators']:
            value=evaluator(input=item['input'], output=output)
            scores.extend(value if isinstance(value,list) else [value])
        return SimpleNamespace(name='todo-agent',run_name='todo-agent - 2026-10-15T12:00:00Z',
                               item_results=[SimpleNamespace(item=item,output=output,evaluations=scores,trace_id=None)])
    client=SimpleNamespace(run_experiment=experiment,flush=lambda:None)
    monkeypatch.setattr(evals,'connect',lambda:(client,False))
    evals.main(['--case','read-fresh','--repeat','1'])
    records=read_runs(tmp_path)
    assert len(records)==1 and records[0]['attempts'][0]['passed'] is True
    assert (tmp_path/records[0]['source_snapshot']).is_dir()
    assert (tmp_path/records[0]['partial_records']).is_dir()


def test_audit_never_samples_missing_answers_as_a_pass(tmp_path):
    import audit
    base=dict(case='job',attempt=1,passed=True,truthful=True,answered=None,error=None,
              judge_quote=None,trace_url=None,conversation=[],after={'todos':[]})
    r=dict(started='2026-10-15',cases=[{'name':'job','asks':'A recorded question','expects':'Recorded outcome'}],
           attempts=[base],repeat=1)
    text,failed=audit.digest([(tmp_path/'run.json',r)],greens=1)
    assert failed==0 and '### Inconclusive: job' in text and '### Passed:' not in text
    r['attempts'][0]['answered']=False
    text,failed=audit.digest([(tmp_path/'run.json',r)],greens=1)
    assert failed==1 and '### Failed: job' in text


def test_token_interruption_is_missing_evidence_not_an_application_crash(monkeypatch):
    import evals
    from model_usage import TokenLimitReached
    class Agent:
        def __init__(self,*args,**kwargs): self.tool_log=[]
        def ask(self,*args): raise TokenLimitReached('allowance reached')
    monkeypatch.setattr(evals,'Agent',Agent)
    output=evals.play('read-fresh')
    assert output['harness_stop']=='allowance reached' and output['error'] is None
    assert output['after'] is not None
    @evals.with_attempt_evidence
    def should_not_grade(**kwargs): pytest.fail('a stopped scenario must not be graded as completed')
    assert should_not_grade(input={'case':'read-fresh','attempt':1},output=output)==[]


def test_persona_snapshot_prices_are_explicit_and_unknown_cache_writes_stay_unknown():
    rows=[{'purpose':'persona','served_model':'gpt-4.1-mini-2025-04-14',
           'usage':{'prompt_tokens':1000,'completion_tokens':100,
                    'prompt_tokens_details':{'cached_tokens':500}}}]
    assert estimate(rows)['usd']==pytest.approx(.00041)
    rows[0]['usage']['prompt_tokens_details']['cache_write_tokens']=100
    assert estimate(rows)['usd'] is None
    assert estimate(rows)['input_tokens']==1000


def test_nonstandard_tiers_are_not_mispriced():
    row={'purpose':'agent','served_model':'gpt-6-luna','service_tier':'priority',
         'usage':{'prompt_tokens':1000,'completion_tokens':100}}
    assert estimate([row])['usd'] is None
