"""A portable review must preserve scores, bind notes to evidence and escape content."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from eval_collection import render, validate
from run_evidence import digest

BUNDLE = Path(__file__).parent/'examples/evaluation-review/collection.json'


def sealed(bundle):
    bundle['bundle_digest']=digest({k:v for k,v in bundle.items() if k!='bundle_digest'})
    return bundle


def test_offline_example_reconciles_and_keeps_original_grades():
    b=json.loads(BUNDLE.read_text());before=deepcopy(b)
    page=render(b)
    assert b==before
    assert len(b['observations'])==20
    assert sum(o['expected'] for o in b['observations'])==3060
    assert sum(o['passed'] for o in b['observations'])==2956
    assert 'quality baseline not accepted' in page
    assert 'Illustrative candidate limits' in page
    assert 'fetch(' not in page and '<script src=' not in page
    assert len(b['examples'])==8


def test_exported_evidence_cannot_silently_change_or_attach_to_another_run():
    b=json.loads(BUNDLE.read_text());b['observations'][0]['passed']+=1
    with pytest.raises(ValueError,match='digest'):validate(b)
    with pytest.raises(ValueError,match='reconcile'):validate(sealed(b))
    b=json.loads(BUNDLE.read_text());b['examples'][0]['source_digest']='wrong'
    with pytest.raises(ValueError,match='original run'):validate(sealed(b))


def test_untrusted_conversation_and_title_cannot_insert_html_or_script():
    b=json.loads(BUNDLE.read_text());payload='</script><script>alert("bad")</script>'
    b['title']=payload;b['examples'][0]['attempt']['conversation'][0]['assistant']=payload
    page=render(sealed(b))
    assert payload not in page
    assert '&lt;/script&gt;' in page and '\\u003c/script\\u003e' in page
    assert page.count('<script>')==1


def test_review_notes_are_bound_to_exact_bundle_and_do_not_relabel():
    from eval_collection import validate_notes
    b=json.loads(BUNDLE.read_text())
    notes={'version':1,'bundle_digest':b['bundle_digest'],
           'reviews':[{'id':x['id'],'assessment':'unreviewed','note':''} for x in b['examples']]}
    assert validate_notes(b,notes)==0
    notes['reviews'][0]['assessment']='grader_concern'
    assert validate_notes(b,notes)==1
    notes['reviews'].append(notes['reviews'][0])
    with pytest.raises(ValueError,match='exactly once'):validate_notes(b,notes)
    notes['bundle_digest']='different'
    with pytest.raises(ValueError,match='different evidence'):validate_notes(b,notes)
