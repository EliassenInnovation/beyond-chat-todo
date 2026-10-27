# Maintain the guide and sample

This file lists the work that keeps the guide and the Todo sample accurate after release.
It is excluded from the published site. [BUILDING.md](BUILDING.md) explains how to build the
site and exports.

## Before release

- Test the checklist builder in Chrome and Safari: keyboard navigation through the checks,
  the partly selected state of group checkboxes, both downloads, and loading a downloaded
  `agent-checks.md` back in.
- Obtain approval to release under the MIT license and to publish in the Eliassen Innovations
  GitHub organization.

## On release day

1. Replace "All rights reserved. Confidential draft." in `LICENSE` and in the README's License
   section with the MIT license text, "Copyright (c) 2026 Eliassen Group". Keep the TodoMVC
   CSS credit and `licenses/todomvc-app-css.txt`.
2. Transfer the repository to the Eliassen Innovations organization. Update every
   `bobfischer` address: `site_url` and `repo_url` in `mkdocs.yml`, the README, and the clone
   command in `docs/guide/start.md`. Code links in the checklist builder follow `repo_url`.
3. Make the repository public. Turn on GitHub secret scanning and push protection, and
   Dependabot alerts.
4. Optional: ask GitHub Support to purge cached views of commits from before the October 24,
   2026 history rewrite, which removed an earlier persona-runner screenshot.
5. Rebuild the site, the PDF, and the Word exports from the released commit. Refresh dated
   statements that should read as of release, such as "no release as of October 3, 2026"
   for the OpenTelemetry GenAI conventions in `docs/reference/inspection.md`.
6. Decide who answers issues and pull requests.

## With every change

- **A check is added or reworded.** Keep existing check IDs; give a new check a new ID.
  Add its `<!-- builder: ... -->` tag (the build fails without one) and describe the change
  in the check revision note in `docs/principles/implementation.md`. Then re-run the
  sample assessment (below).
- **Todo application code changes.** Run the offline tests. If the change can affect what
  the model sees or does, run the visible eval suite, and record a model or configuration
  change as a new comparison period instead of reusing old control limits.
- **A screenshot is added or replaced.** Check every visible value for personal or client
  data before committing. Advisor screenshots should use persona data unless real data is
  a deliberate choice. Once the repository is public, removing an image means rewriting
  history.
- **The default models change.** Update `todo/model_provider.py`, the model guide, and
  `model_rates.example.json` together; a test fails if the example file misses a default
  model. The repository ships no prices.

## Re-run the sample assessment

`docs/guides/sample-assessment.md` rates the Todo sample against every acceptance check.
Re-run it after the checks or the application change, and state the commit and date
assessed. Use only the results Pass, Fail, Not run, and Not applicable. The checklist
builder can produce the handoff: choose Everything, give `agent-checks.md` to a coding
agent, and ask it to report results in the page's table format.

## Every quarter

- **Model availability.** Confirm the default models in `todo/model_provider.py` are still
  offered by each provider. When a provider changes a model, run three full eval runs and
  compare individual cases before assuming behavior is unchanged.
- **Dated facts.** Refresh the "Development snapshot" in `docs/guides/models.md`, the
  OpenTelemetry release status in `docs/reference/inspection.md`, and the cited MCP
  specification versions (2026-07-28 for the core specification, 2026-01-26 for MCP Apps).
- **External links.** The strict build checks internal links and anchors only. Check
  external links (provider pricing pages, papers, vendor documentation) separately.
- **Dependencies.** The Langfuse SDK is pinned in `requirements.txt`; after upgrading it,
  verify local records and trace export. Review dependency and security alerts.
- **Exports.** Rebuild the PDF and Word exports when the site content has changed, so the
  "Download the last PDF export" link matches the site.

Model availability, external links, and export rebuilds can run as a scheduled CI job.
Re-running the assessment and reviewing screenshots need a person.

## Optional improvements not yet made

- Give `evaluations.evals` a default `--max-tokens` allowance, as the persona runner has.
