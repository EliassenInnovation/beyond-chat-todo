#!/usr/bin/env bash
# Review the complete site locally; changes reload the browser automatically.
set -euo pipefail
cd "$(dirname "$0")"
if [[ "${1:-}" == "--help" ]]; then
  echo 'Usage: ./preview.sh [port]  (default: 8000)'
  exit 0
fi
if [[ ! -x .venv-docs/bin/python ]]; then
  python3 -m venv .venv-docs
fi
if ! .venv-docs/bin/python -c 'import mkdocs, material, livereload' 2>/dev/null; then
  .venv-docs/bin/python -m pip install -r requirements-docs.txt
fi
exec .venv-docs/bin/python scripts/preview_docs.py "${1:-8000}"
