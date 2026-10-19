"""Offline tests use stand-ins, independently of a developer's local settings."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Set this before importing modules that select models at import time.
for name in tuple(os.environ):
    if name.startswith('EVALBASICS_'):
        del os.environ[name]
os.environ['EVALBASICS_PROVIDER'] = 'openai'
os.environ['LANGFUSE_TRACING_ENABLED'] = 'false'
os.environ['OPENAI_API_KEY'] = 'offline-test-key'
os.environ['ANTHROPIC_API_KEY'] = 'offline-test-key'

from todo import langfuse_setup

# Explicit fixture files still work in configuration tests.
langfuse_setup.ENV_FILES = ()
