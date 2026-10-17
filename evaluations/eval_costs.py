"""Estimated standard API cost from reported usage; never a billing ledger.

Verified 2026-10-15:
https://developers.openai.com/api/docs/guides/decisions
https://developers.openai.com/api/docs/models/gpt-6-luna
https://developers.openai.com/api/docs/models/gpt-4.1-mini
Additional rates verified 2026-10-16:
https://developers.openai.com/api/docs/models/gpt-6-sol
https://docs.typesafe.ai/models
Claude Haiku 5.5 rates verified 2026-10-16:
https://platform.claude.com/docs/en/models/haiku-5-5/overview
Unknown models or missing usage stay unknown. Cached tokens are a subset of input.
"""
RATES = {'gpt-6-sol': {'input': 2.00, 'cached': 0.20, 'cache_write': 2.50, 'output': 10.00},
         'gpt-6-luna': {'input': 0.10, 'cached': 0.01, 'cache_write': 0.125, 'output': 0.50},
         'gpt-4.1-mini': {'input': 0.40, 'cached': 0.10, 'cache_write': None, 'output': 1.60}}
RATES['gpt-4.1-mini-2025-04-14'] = RATES['gpt-4.1-mini']


def estimate(generations):
    if not generations:
        return dict(usd=None, complete=False, input_tokens=0, output_tokens=0, cached_tokens=0)
    total, inputs, outputs, cached, complete = 0.0, 0, 0, 0, True
    for g in generations:
        usage = g.get('usage') or {}
        rate = RATES.get(g.get('served_model'))
        if g.get('purpose') == 'guard':
            # Decisions and Jev bill input only; rates are provider/model specific.
            guard_rate = {'gpt-6-luna': 0.10, 'jev-1.14.0': 0.042}.get(g.get('served_model'))
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
            if (g.get('error') or g.get('served_model') != 'claude-haiku-5-5'
                    or inp + cache + writes > 100000
                    or g.get('service_tier') not in (None, 'default', 'standard')):
                complete = False
                continue
            total += (inp * 0.10 + out * 0.50 + cache * 0.01 + (writes-hour) * 0.125 + hour * 0.20) / 1e6
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
                complete=complete, input_tokens=inputs, output_tokens=outputs, cached_tokens=cached,
                rates_date='2026-10-16', assumption='Standard processing; reported responses only; excludes unreported retries and other charges.')
