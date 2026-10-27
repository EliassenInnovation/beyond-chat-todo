#!/usr/bin/env bash
# Explicit release: commit documentation, push, build web + PDF, check and deploy.
set -euo pipefail
cd "$(dirname "$0")"
if [[ "${1:-}" == "--help" ]]; then
  cat <<'HELP'
Usage: ./publish.sh [commit message]
Commits documentation/release files only, pushes main, and waits for GitHub Actions
 to build the website and a fresh PDF, check links, and deploy both together.
Requires git and authenticated GitHub CLI (gh). Application/test edits are untouched.
Review with ./preview.sh first. No publication happens during local preview.
HELP
  exit 0
fi
command -v gh >/dev/null || { echo 'Install GitHub CLI and run gh auth login.' >&2; exit 1; }
[[ "$(git branch --show-current)" == main ]] || { echo 'Publish from main.' >&2; exit 1; }
if ! git diff --cached --quiet; then
  echo 'Commit or unstage existing staged changes before publishing.' >&2
  exit 1
fi
git diff --check
paths=(docs mkdocs.yml requirements-docs.txt .github/docs_hooks.py .github/check_docs.py
       .github/workflows/evaluation-pages.yml scripts/preview_docs.py scripts/prepare_docs_site.py
       preview.sh publish.sh)
git add -- "${paths[@]}"
if ! git diff --cached --quiet; then
  git commit -m "${1:-Publish guide updates}"
fi
revision=$(git rev-parse HEAD)
git push origin main
requested_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
gh workflow run evaluation-pages.yml --ref main -f build_pdf=true -f expected_sha="$revision"
echo "Full release requested for $revision (including PDF)."
run_id=''
for attempt in {1..20}; do
  run_id=$(gh run list --workflow evaluation-pages.yml --event workflow_dispatch --limit 20 \
    --json databaseId,displayTitle,createdAt --jq ".[] | select(.displayTitle == \"Publish guide $revision\") | select(.createdAt >= \"$requested_at\") | .databaseId" | head -n 1)
  [[ -n "$run_id" ]] && break
  sleep 2
done
[[ -n "$run_id" ]] || { echo 'Could not find release run. Check gh run list.' >&2; exit 1; }
gh run watch "$run_id" --exit-status
echo "Published website and fresh PDF: $(python3 scripts/site_urls.py site)"
