"""The only Langfuse setup in the project.

The SDK reads its settings from environment variables (LANGFUSE_PUBLIC_KEY,
LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL, LANGFUSE_TRACING_ENVIRONMENT, LANGFUSE_RELEASE),
and get_client() returns the one client for the process. connect() fills those
variables from .env; score_config_ids() makes sure the score configs exist.

One deliberate addition to the documented setup: if Langfuse is not reachable,
tracing is switched off and everything still runs. The evals grade in code;
Langfuse is where you look at the results, not where they are decided.
"""

import os
from pathlib import Path

import httpx
from langfuse import Langfuse, LangfuseOtelSpanAttributes, get_client, is_default_export_span

# Configuration belongs to this project; never borrow another app's credentials.
ENV_FILES = (Path(__file__).parent / '.env',)
KEYS = ('LANGFUSE_PUBLIC_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_BASE_URL')

# Every score this project sends, declared once. Langfuse validates scores against their
# config, charts them consistently, and lets a person score a trace with the same yes/no.
SCORE_CONFIGS = {
    'passed': 'The saved todo list is what the case expects (graded in code).',
    'claims_match_outcome': 'Every change the replies claim is in the saved list (graded by a model).',
    'claims_real_abilities': 'No reply claims, offers or accepts an ability the app lacks, or stays silent when asked for one (a model, plus code for silence).',
    'claims_real_approvals': 'No reply claims or asks for an approval that is not waiting (graded by a model).',
    'answers_every_part': 'Every request and question in each message gets a response (graded by a model).',
    'receipts_repeated': "Each reply says the app's own sentence about every change word for word (graded in code).",
}


def load_env(paths=ENV_FILES, environ=os.environ):
    """Copy KEY=value lines into environ. Real environment variables and earlier files win."""
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            key, sep, value = line.strip().partition('=')
            if sep and value and not key.startswith('#'):
                environ.setdefault(key, value.strip().strip('"\''))


def setting(name, default):
    """Read a setting before model modules initialize; environment wins over this repo's .env."""
    values = {}
    load_env(environ=values)
    return os.environ.get(name, values.get(name, default))


def server_up(base_url):
    try:
        return httpx.get(f'{base_url}/api/public/health', timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


def connect(should_export_span=None, opt_in=False):
    """Configure and return (client, live). Call once, before anything is traced.

    should_export_span decides which spans leave the process; the app passes one that keeps a
    person's own chat out of Langfuse (see app.py).
    opt_in: trace only when LANGFUSE_TRACING_ENABLED=true is set. The app passes it: a trace is a copy
    of what was said, so where real people type, tracing is off until someone turns it on on purpose.
    The evals and personas make synthetic conversations, so they trace whenever Langfuse is there.
    """
    load_env()
    os.environ.setdefault('LANGFUSE_TRACING_ENVIRONMENT', 'development')
    os.environ.setdefault('LANGFUSE_RELEASE', 'evalbasics')
    enabled = os.environ.get('LANGFUSE_TRACING_ENABLED', '').lower()
    chosen = enabled == 'true' if opt_in else enabled != 'false'
    live = chosen and all(os.environ.get(key) for key in KEYS) and server_up(os.environ['LANGFUSE_BASE_URL'])
    if not live:
        print('(Tracing off: not turned on.)' if not chosen else '(Langfuse not reachable: running without tracing.)')
        os.environ['LANGFUSE_TRACING_ENABLED'] = 'false'
        for key in KEYS[:2]:
            os.environ.setdefault(key, 'off')  # a disabled client still wants keys
    if should_export_span:
        Langfuse(should_export_span=should_export_span)  # the first client made is the one get_client() returns
    return get_client(), live


# The sessions that are recorded: a persona's, and an exploratory tester's (chosen, and shown on screen).
RECORDED_SESSIONS = ('persona-', 'tester-')


def synthetic_only(span):
    """Export a span only if it belongs to a persona's or an exploratory tester's chat (RECORDED_SESSIONS).

    Langfuse holds the evals and persona chats, including what a tester types into one (the app
    shows "Recording to Langfuse" when this would send); a chat of your own is never sent.
    """
    session = (span.attributes or {}).get(LangfuseOtelSpanAttributes.TRACE_SESSION_ID, '')
    return is_default_export_span(span) and str(session).startswith(RECORDED_SESSIONS)


def score_config_ids(client):
    """Create any missing score config; return {name: config id}.

    Refuses to reuse a config of the same name but a different type: the server would
    reject every score sent against it, and the SDK only logs that in the background.
    """
    existing, page = {}, 1
    while True:
        batch = client.api.score_configs.get(page=page, limit=100)
        existing.update({c.name: c for c in batch.data if not c.is_archived})
        if page >= batch.meta.total_pages:
            break
        page += 1
    ids = {}
    for name, description in SCORE_CONFIGS.items():
        config = existing.get(name)
        if config is None:
            config = client.api.score_configs.create(name=name, data_type='BOOLEAN', description=description)
        elif config.data_type != 'BOOLEAN':
            raise RuntimeError(f'Score config {name!r} exists as {config.data_type}, not BOOLEAN; '
                               'rename one of them.')
        ids[name] = config.id
    return ids
