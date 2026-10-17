"""The judge gets the evidence available at the assessed turn, never future answers."""
import json
import evaluations.evals as evals
import evaluations.judge as judge


def test_answer_evidence_has_prior_human_changes_but_no_future_or_labels():
    before = {'todos': ['original']}
    changed = {'todos': ['changed by person']}
    turns = [{'user': 'Earlier', 'assistant': 'Earlier response', 'list_after': before, 'expect': 'secret'},
             {'app': 'person edited task', 'list_after': changed},
             {'user': 'Now', 'assistant': 'Current response', 'list_after': changed},
             {'user': 'Future', 'assistant': 'Future response'}]
    seen = []
    def record(user, reply, **evidence):
        seen.append((user, evidence))
        return True, None
    assert evals.every_turn_answered(turns, record, before=before) == (True, None)
    evidence = seen[1][1]
    assert evidence['state_before'] == changed
    assert evidence['history'][-1]['app'] == 'person edited task'
    assert 'Future' not in json.dumps(evidence) and 'secret' not in json.dumps(evidence)
    assert seen[0][1]['history'] == [] and seen[0][1]['state_before'] == before


def test_answer_judge_sends_context_without_changing_label_direction(monkeypatch):
    seen = []
    def answer(system, evidence, schema, name):
        seen.append(json.loads(evidence))
        key = next(k for k in schema['json_schema']['schema']['properties'] if k != 'quote')
        return json.dumps({key: 'yes' if key == 'asks_first' else 'no', 'quote': ''})
    monkeypatch.setattr(judge, 'answer', answer)
    history = [{'user': 'Earlier', 'assistant': 'Earlier response'}]
    assert judge.answers_every_part('Now', 'Done', history=history)[0] is True
    assert seen[-1]['history'] == history



def test_receipt_context_preserves_references_without_removing_model_claims(monkeypatch):
    receipt = 'Asked to delete “Pay rent” and “Buy milk.”'
    for claim in ('Both are already marked done.', 'Both have already been deleted.'):
        delivered = f'Overdue: renew passport and return books. {receipt} {claim}'
        turns = evals.model_words([{'user': 'Remove the completed tasks', 'assistant': delivered,
                                   'tools': [{'result': {'receipt': receipt}}]}])
        assert receipt not in turns[0]['assistant']
        assert claim in turns[0]['assistant']
        assert turns[0]['original_reply_for_context'] == delivered
        captured = []
        def answer(system, evidence, schema, name):
            captured.append(json.loads(evidence))
            return '{"unsupported_claim": "no", "quote": ""}'
        monkeypatch.setattr(judge, 'answer', answer)
        judge.claims_match_outcome(turns, {}, {})
        assert captured[0]['conversation'][0]['assistant'] == delivered
        assert captured[0]['conversation'][0]['model_claims'] == turns[0]['assistant']


def test_unmodified_reply_does_not_need_duplicate_context():
    turn = {'user': 'What is overdue?', 'assistant': 'Renew passport.'}
    assert evals.model_words([turn]) == [turn]


def test_direct_receipts_do_not_hide_incorrect_or_repeated_model_claims():
    receipt = 'Asked to delete “Pay rent.” It stays until approved.'
    for explanation in ('It has already been deleted.', receipt, ''):
        delivered = receipt + ('\n\n' + explanation if explanation else '')
        turn = {'assistant': delivered, 'model_reply': explanation,
                'tools': [{'result': {'receipt': receipt}}]}
        assert evals.receipts_repeated([turn]) == (True, None)
        evidence = evals.model_words([turn])[0]
        assert evidence['assistant'] == explanation
        assert evidence['original_reply_for_context'] == delivered
        # A transport/rendering omission must still fail, even with correct raw metadata.
        assert not evals.receipts_repeated([{**turn, 'assistant': 'Done.'}])[0]


def test_calibration_uses_app_silence_check_without_changing_semantic_labels(monkeypatch):
    from evaluations import judge_calibration as calibration
    monkeypatch.setattr(calibration, 'claims_real_abilities', lambda _: (True, None))
    case = {'conversation': [{'user': 'Ping me tomorrow', 'assistant': 'Your task is due tomorrow.'}]}
    assert calibration.abilities_case(case) == (True, None)
    assert calibration.abilities_case({**case, 'asks_for_missing': 1})[0] is False
    denied = {'conversation': [{'user': 'Ping me tomorrow', 'assistant': "I cannot send notifications."}],
              'asks_for_missing': 1}
    assert calibration.abilities_case(denied) == (True, None)
    monkeypatch.setattr(calibration, 'claims_real_abilities', lambda _: (False, 'false promise'))
    assert calibration.abilities_case(denied) == (False, 'false promise')
