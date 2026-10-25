"""Estimated API cost from reported usage and rates you supply; never a billing ledger.

The sample ships no prices. To estimate cost, copy model_rates.example.json to model_rates.json
at the repository root and fill in your provider's current rates (USD per million tokens).
Without that file, or for a model left blank, cost stays unknown and token counts are still
reported. Unknown models or missing usage stay unknown.
A compatible provider reusing a recognized model ID may charge different rates; these
estimates do not distinguish providers.
OpenAI cached tokens are a subset of input;
Anthropic cache reads and writes are additional to uncached input.
"""
import json
from pathlib import Path

RATES_FILE = Path(__file__).resolve().parents[1] / 'model_rates.json'
OPENAI_FIELDS = ('input', 'cached', 'cache_write', 'output')
ANTHROPIC_FIELDS = ('input', 'output', 'cached', 'write_5m', 'write_1h')


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


def load_rates(path=None):
    """The rates file as {'openai', 'anthropic', 'guards', 'rates_date', 'source'}; empty when absent.

    A model counts as priced only when every required rate is a number. OpenAI's cache_write may
    be null for a model with no cache-write price. A malformed file raises, naming the file."""
    path = Path(path) if path else RATES_FILE
    empty = dict(openai={}, anthropic={}, guards={}, rates_date=None, source=None)
    if not path.exists():
        return empty
    try:
        data = json.loads(path.read_text())
    except ValueError as exc:
        raise ValueError(f'{path} is not valid JSON: {exc}') from None
    if not isinstance(data, dict):
        raise ValueError(f'{path} must contain a JSON object.')
    rates = dict(empty, rates_date=data.get('rates_date'), source=path.name)
    for section, fields in (('openai', OPENAI_FIELDS), ('anthropic', ANTHROPIC_FIELDS)):
        for model, entry in (data.get(section) or {}).items():
            if not isinstance(entry, dict):
                raise ValueError(f'{path}: {section}.{model} must be an object of rates.')
            optional = ('cache_write',) if section == 'openai' else ()
            if all(_number(entry.get(f)) or (f in optional and entry.get(f) is None) for f in fields):
                rates[section][model] = {f: entry.get(f) for f in fields}
    for model, rate in (data.get('guards') or {}).items():
        if _number(rate):
            rates['guards'][model] = rate
    return rates


def estimate(generations, rates=None):
    rates = load_rates() if rates is None else rates
    openai_rates, anthropic_rates, guard_rates = rates['openai'], rates['anthropic'], rates['guards']
    provenance = dict(rates_date=rates.get('rates_date'), rates_source=rates.get('source'),
                      assumption='Standard processing; reported responses only; excludes unreported retries and other charges.')
    if not generations:
        return dict(usd=None, complete=False, input_tokens=0, output_tokens=0, cached_tokens=0, **provenance)
    total, inputs, outputs, cached, complete = 0.0, 0, 0, 0, True
    for g in generations:
        usage = g.get('usage') or {}
        rate = openai_rates.get(g.get('served_model'))
        if g.get('purpose') == 'guard':
            # Decisions-style guards bill input only; rates are provider/model specific.
            guard_rate = guard_rates.get(g.get('served_model'))
            inp = usage.get('input_tokens')
            out = usage.get('output_tokens', 0)
            if (g.get('error') or guard_rate is None
                    or not isinstance(inp, int) or isinstance(inp, bool) or not 0 <= inp <= 272000
                    or not isinstance(out, int) or isinstance(out, bool) or out < 0
                    or g.get('service_tier') not in (None, 'default', 'standard')):
                complete = False
                continue
            inputs += inp; outputs += out
            total += inp * guard_rate / 1e6
            continue
        if {'input_tokens', 'output_tokens'} <= usage.keys():
            # Anthropic reports cache reads/writes separately from uncached input.
            inp, out = usage['input_tokens'], usage['output_tokens']
            cache = usage.get('cache_read_input_tokens') or 0
            writes = usage.get('cache_creation_input_tokens') or 0
            detail = usage.get('cache_creation') or {}
            hour = detail.get('ephemeral_1h_input_tokens') or 0
            if any(type(v) is not int or v < 0 for v in (inp, out, cache, writes, hour)) or hour > writes:
                complete = False
                continue
            inputs += inp + cache + writes; outputs += out; cached += cache
            native_rate = anthropic_rates.get(g.get('served_model'))
            if (g.get('error') or native_rate is None
                    or inp + cache + writes > 100000
                    or g.get('service_tier') not in (None, 'default', 'standard')):
                complete = False
                continue
            total += (inp * native_rate['input'] + out * native_rate['output'] + cache * native_rate['cached']
                      + (writes-hour) * native_rate['write_5m'] + hour * native_rate['write_1h']) / 1e6
            continue
        if not {'prompt_tokens', 'completion_tokens'} <= usage.keys():
            complete = False
            continue
        inp, out = usage['prompt_tokens'], usage['completion_tokens']
        details = usage.get('prompt_tokens_details') or {}
        cache = details.get('cached_tokens') or 0
        writes = details.get('cache_write_tokens') or 0
        if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in (inp, out, cache, writes)) or cache + writes > inp:
            complete = False
            continue
        inputs += inp; outputs += out; cached += cache
        # Token counts remain useful even when a model or call cannot be priced.
        # This sample prices only short-context, standard processing.
        if (g.get('error') or not rate or inp > 272000
                or g.get('service_tier') not in (None, 'default', 'standard')
                or (writes and rate['cache_write'] is None)):
            complete = False
            continue
        total += ((inp-cache-writes)*rate['input']+cache*rate['cached']+writes*(rate['cache_write'] or 0)+out*rate['output'])/1e6
    return dict(usd=round(total, 8) if complete else None, known_usd=round(total, 8),
                complete=complete, input_tokens=inputs, output_tokens=outputs, cached_tokens=cached, **provenance)


def rates_note(rates=None):
    """One sentence for reports: where the estimate's rates came from, or how to supply them."""
    rates = load_rates() if rates is None else rates
    if not any(rates[k] for k in ('openai', 'anthropic', 'guards')):
        return ('No model rates were supplied, so cost is not estimated; token counts are shown. To estimate cost, '
                'copy model_rates.example.json to model_rates.json and fill in your provider\'s current rates.')
    dated = f" dated {rates['rates_date']}" if rates.get('rates_date') else ''
    return (f"Cost estimates use the rates you supplied in {rates['source']}{dated}. Unreported retries and other charges "
            'are excluded; unknown usage or models remain unpriced. Your provider\'s billing is authoritative.')
