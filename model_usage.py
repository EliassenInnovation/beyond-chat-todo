"""Optional local token accounting. No prompts, credentials, or tracing service required."""
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from threading import RLock
import time

_CURRENT = ContextVar('model_usage', default=None)
_ATTEMPT = ContextVar('model_attempt', default=None)


class TokenLimitReached(Exception):
    """Stop before another call; the preceding call may have exceeded the allowance."""


@dataclass
class Usage:
    limit: int | None
    calls: list = field(default_factory=list)
    on_update: object = None
    lock: object = field(default_factory=RLock)

    def check(self):
        if self.limit is None:
            return
        if any(c['tokens'] is None for c in self.calls):
            raise TokenLimitReached('Token usage unavailable; stopped before another model call.')
        if self.total >= self.limit:
            raise TokenLimitReached('Token allowance reached; stopped before another model call.')

    @property
    def total(self):
        return sum(c['tokens'] or 0 for c in self.calls)

    def summary(self):
        return dict(token_allowance=self.limit, reported_tokens=self.total,
                    complete=all(c['tokens'] is not None for c in self.calls), calls=list(self.calls))


@contextmanager
def capture(limit=None, on_update=None):
    if limit is not None and limit < 1:
        raise ValueError('Token allowance must be positive.')
    usage = Usage(limit, on_update=on_update)
    token = _CURRENT.set(usage)
    try:
        yield usage
    finally:
        _CURRENT.reset(token)


@contextmanager
def attempt(case, number):
    token = _ATTEMPT.set({'case': case, 'attempt': number})
    try:
        yield
    finally:
        _ATTEMPT.reset(token)


def call_model(call, *, purpose, **kwargs):
    usage = _CURRENT.get()
    if usage is None:
        return call(**kwargs)
    with usage.lock:
        usage.check()
    started = time.monotonic()
    response, error = None, None
    try:
        response = call(**kwargs)
        return response
    except Exception as exc:
        error = type(exc).__name__
        raise
    finally:
        raw = getattr(response, 'usage', None)
        data = raw.model_dump() if hasattr(raw, 'model_dump') else None
        tokens = None
        if data:
            tokens = data.get('total_tokens')
            if tokens is None and 'input_tokens' in data and 'output_tokens' in data:
                tokens = sum(data.get(k) or 0 for k in ('input_tokens', 'output_tokens',
                             'cache_creation_input_tokens', 'cache_read_input_tokens'))
        with usage.lock:
            usage.calls.append(dict(purpose=purpose, requested_model=kwargs.get('model'),
                                    served_model=getattr(response, 'model', None), tokens=tokens, usage=data,
                                    error=error, system_fingerprint=getattr(response, 'system_fingerprint', None), service_tier=getattr(response, 'service_tier', None), duration_seconds=round(time.monotonic() - started, 4),
                                    **(_ATTEMPT.get() or {})))
            if usage.on_update:
                usage.on_update(usage.summary())
