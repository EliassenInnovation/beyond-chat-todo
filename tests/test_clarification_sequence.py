from copy import deepcopy

import evaluations.evals as evals
from test_main import GOOD_AND_BAD, state, MOM, PLUMBER

CASE = 'clarify-then-do-v2'


def example():
    output = deepcopy(GOOD_AND_BAD[CASE][0])
    output['conversation'][0]['list_after'] = deepcopy(output['before'])
    return output


def test_correct_final_state_does_not_excuse_changing_before_clarification():
    output = example()
    output['conversation'][0]['list_after'] = output['after']
    assert evals.grade(CASE, output) is False
    verdict, reason = evals.clarification_state(output, 1)
    assert verdict is False and 'before clarification' in reason


def test_question_and_checkpoint_are_both_required():
    output = example()
    output['clarification_passed'] = False
    assert evals.grade(CASE, output) is False
    output['clarification_passed'] = None
    assert evals.grade(CASE, output) is None
    output['clarification_passed'] = True
    del output['conversation'][0]['list_after']
    assert evals.grade(CASE, output) is None
    # A known wrong final state must not be hidden by a missing judgment.
    output['after'] = state((MOM, PLUMBER))
    assert evals.grade(CASE, output) is False


def test_highlight_is_harmless_but_pending_delete_is_not():
    output = example()
    output['conversation'][0]['list_after']['pointed_at'] = 'active'
    assert evals.grade(CASE, output) is True
    output['conversation'][0]['list_after']['waiting_for_approval'] = [{'todo_id': 1}]
    assert evals.grade(CASE, output) is False


def test_selected_turn_uses_nearest_state_and_only_its_reply(monkeypatch):
    output = example()
    person_state = deepcopy(output['before'])
    person_state['todos'][1]['done'] = True
    output['conversation'][0]['list_after'] = deepcopy(person_state)
    output['conversation'].insert(0, {'app': 'Person changes the list', 'list_after': person_state})
    output['conversation'].append({'user': 'Mom', 'assistant': 'Done', 'list_after': output['after']})
    seen = []
    monkeypatch.setattr(evals, 'asks_first', lambda *args: (seen.append(args) or True, 'Which call?'))
    assert evals.judge_clarification(output, 1) == (True, 'Which call?')
    assert len(seen) == 1 and seen[0][1] == 'Which call?'
    output['conversation'][1]['list_after'] = output['after']
    assert evals.judge_clarification(output, 1)[0] is False
    assert len(seen) == 1  # no paid judge needed for a demonstrated early change


def test_missing_intermediate_state_is_not_replaced_by_stale_initial_state():
    output = example()
    output['conversation'].insert(0, {'app': 'Person changes the list'})
    assert evals.clarification_state(output, 1)[0] is None
