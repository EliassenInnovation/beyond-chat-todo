from copy import deepcopy
from evaluations.regrade_answers import apply_verdict


def test_regrade_changes_only_completeness_and_retains_other_failures():
    a={'answered':False,'answered_quote':'old','passed':False,'truthful':True,
       'checks':{'passed':{'passed':False},'answers_every_part':{'passed':False,'reason':'old'}},
       'ungraded':[],'conversation':[{'user':'hi','assistant':'hello'}]}
    before=deepcopy(a);r=apply_verdict(a,True,'')
    assert a==before and r['passed'] is False and r['truthful'] is True
    assert r['answered'] is True and r['answered_quote'] is None
    assert r['conversation']==a['conversation']
    unavailable=apply_verdict(r,None,'unavailable')
    assert unavailable['answered'] is None and 'answers_every_part' in unavailable['ungraded']
    assert 'answers_every_part' not in unavailable['checks']
