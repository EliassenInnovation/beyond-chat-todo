"""Provider profiles, with optional per-role model and provider overrides."""
from todo.langfuse_setup import setting

OPENAI_MODELS = {'agent': 'gpt-6-luna', 'judge': 'gpt-6-luna',
                 'persona': 'gpt-4.1-mini', 'action_guard': 'gpt-6-luna'}
ANTHROPIC_MODELS = {'agent': 'claude-haiku-5-5', 'judge': 'claude-sonnet-5-5',
                    'persona': 'claude-haiku-5-5', 'action_guard': 'claude-haiku-5-5'}
MODEL_KEYS = {'agent': 'EVALBASICS_MODEL', 'judge': 'EVALBASICS_JUDGE_MODEL',
              'persona': 'EVALBASICS_PERSONA_MODEL', 'action_guard': 'EVALBASICS_ACTION_GUARD_MODEL'}


def profile():
    provider = setting('EVALBASICS_PROVIDER', 'openai')
    if provider not in ('openai', 'anthropic'):
        raise ValueError('EVALBASICS_PROVIDER must be openai or anthropic.')
    return provider


def model_for(role):
    default = (ANTHROPIC_MODELS if profile() == 'anthropic' else OPENAI_MODELS)[role]
    return setting(MODEL_KEYS[role], default)


def provider_for(role, model):
    # Without a profile setting, preserve historical model-prefix inference.
    default = setting('EVALBASICS_PROVIDER', 'auto')
    provider = setting(f'EVALBASICS_{role.upper()}_PROVIDER', default)
    if provider == 'auto':
        return 'anthropic' if model.startswith('claude-') else 'openai'
    if provider not in ('openai', 'anthropic'):
        raise ValueError(f'EVALBASICS_{role.upper()}_PROVIDER must be auto, openai, or anthropic.')
    return provider


def merge_guard_mode():
    default = 'boolean' if provider_for('action_guard', model_for('action_guard')) == 'anthropic' else 'decisions'
    mode = setting('EVALBASICS_MERGE_GUARD_MODE', default)
    if mode not in ('boolean', 'decisions'):
        raise ValueError('EVALBASICS_MERGE_GUARD_MODE must be decisions or boolean.')
    return mode
