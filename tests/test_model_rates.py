"""Cost estimates use only rates the person supplies; the repository ships no prices."""
import json
from pathlib import Path

import pytest

from evaluations import eval_costs
from todo import agent, model_provider

ROOT = Path(__file__).resolve().parents[1]
CALL = {'purpose': 'agent', 'served_model': 'gpt-6-luna',
        'usage': {'prompt_tokens': 1000, 'completion_tokens': 200}}


def write(tmp_path, data):
    path = tmp_path / 'model_rates.json'
    path.write_text(json.dumps(data) if not isinstance(data, str) else data)
    return path


def test_without_a_rates_file_cost_is_unknown_and_tokens_still_count(tmp_path):
    rates = eval_costs.load_rates(tmp_path / 'missing.json')
    result = eval_costs.estimate([CALL], rates)
    assert result['usd'] is None and not result['complete']
    assert (result['input_tokens'], result['output_tokens']) == (1000, 200)
    assert 'copy model_rates.example.json to model_rates.json' in eval_costs.rates_note(rates)


def test_the_shipped_example_prices_nothing():
    rates = eval_costs.load_rates(ROOT / 'model_rates.example.json')
    assert not rates['openai'] and not rates['anthropic'] and not rates['guards']
    assert eval_costs.estimate([CALL], rates)['usd'] is None


def test_the_example_lists_every_default_model():
    example = json.loads((ROOT / 'model_rates.example.json').read_text())
    assert set(model_provider.OPENAI_MODELS.values()) <= example['openai'].keys()
    assert set(model_provider.ANTHROPIC_MODELS.values()) <= example['anthropic'].keys()
    assert agent.GUARD_MODEL in example['guards']


def test_supplied_rates_are_used_and_reported_with_their_date(tmp_path):
    path = write(tmp_path, {'rates_date': '2027-01-05', 'openai': {
        'gpt-6-luna': {'input': 1.0, 'cached': 0.1, 'cache_write': None, 'output': 2.0}}})
    rates = eval_costs.load_rates(path)
    result = eval_costs.estimate([CALL], rates)
    assert result['usd'] == pytest.approx((1000 * 1.0 + 200 * 2.0) / 1e6)
    assert (result['rates_date'], result['rates_source']) == ('2027-01-05', 'model_rates.json')
    assert 'model_rates.json dated 2027-01-05' in eval_costs.rates_note(rates)


@pytest.mark.parametrize('entry', [
    {'input': 1.0, 'cached': 0.1, 'cache_write': None, 'output': None},   # a required rate left blank
    {'input': 1.0, 'cached': 0.1, 'cache_write': None},                   # a required rate missing
    {'input': '1.0', 'cached': 0.1, 'cache_write': None, 'output': 2.0},  # not a number
    {'input': -1.0, 'cached': 0.1, 'cache_write': None, 'output': 2.0},   # negative
])
def test_incomplete_entries_leave_the_model_unpriced(tmp_path, entry):
    rates = eval_costs.load_rates(write(tmp_path, {'openai': {'gpt-6-luna': entry}}))
    assert 'gpt-6-luna' not in rates['openai']
    assert eval_costs.estimate([CALL], rates)['usd'] is None


def test_a_malformed_file_names_itself(tmp_path):
    path = write(tmp_path, '{not json')
    with pytest.raises(ValueError, match='model_rates.json'):
        eval_costs.load_rates(path)


def test_personal_rates_are_not_committed():
    assert 'model_rates.json' in (ROOT / '.gitignore').read_text().split()
