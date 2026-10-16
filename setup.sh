#!/usr/bin/env bash
# Portable local setup. No shell-profile edits, vault access, or services started.
set -euo pipefail
cd "$(dirname "$0")"
python_bin="${PYTHON:-python3}"
"$python_bin" -c 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ required"'
if [ ! -d .venv ]; then
  "$python_bin" -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.txt
if [ ! -e .env ]; then cp .env.example .env; fi
printf '%s\n' 'Ready. Run .venv/bin/python -m streamlit run todo/app.py --server.address 127.0.0.1'
