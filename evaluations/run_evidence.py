"""Local evidence for comparing runs. Captures metadata, never prompts or credentials."""
from todo.model_usage import attempt, capture
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def configuration(root, *, cases, repeat, model, judge_model, guards, inject, shuffled):
    """Frozen before the first call. Dirty commits alone cannot identify what was tested."""
    files = ['todo/agent.py', 'todo/guard_check.py', 'todo/capabilities.py', 'todo/todos.py', 'todo/view.py', 'evaluations/judge.py', 'evaluations/evals.py',
             'evaluations/run_evidence.py', 'todo/model_usage.py', 'evaluations/eval_monitor.py', 'evaluations/eval_costs.py', 'evaluations/persona_report.py', 'todo/langfuse_setup.py', 'requirements.txt']
    source = {name: hashlib.sha256((Path(root) / name).read_bytes()).hexdigest() for name in files}
    packages = {}
    for name in ('openai', 'anthropic', 'langfuse'):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = 'not installed'
    settings = dict(source=source, packages=packages, python=platform.python_version(),
                    cases=list(cases), repeat=repeat, model=model, judge_model=judge_model,
                    guards=sorted(guards), inject=inject, shuffled=shuffled)
    # A configurable guard model is part of the process being measured, not just its source code.
    import todo.guard_check as guard_check
    from todo.capabilities import REGISTRY
    chat_guards = {g.name for g in REGISTRY.guards if g.provider == 'chat'}
    if chat_guards.intersection(guards):
        settings['action_guard_model'] = guard_check.MODEL
        settings['action_guard_settings'] = dict(guard_check.SETTINGS)
    # Compare endpoint configuration without recording credentials embedded in a custom URL.
    settings['provider_endpoints'] = {key: digest(os.environ.get(key, default)) for key, default in (
        ('OPENAI_BASE_URL', 'https://api.openai.com/v1'), ('ANTHROPIC_BASE_URL', 'https://api.anthropic.com'))}
    return {'fingerprint': digest(settings), 'settings': settings}
