<span id="optional-langfuse-integration"></span>

# Optional tracing

This repository uses Langfuse to illustrate trace inspection and experiment exploration. It does
not claim that Langfuse is the tool you should choose. Cases, graders, saved outcomes,
usage records, HTML reports, and monitoring rules are stored in the repository and work without a
Langfuse account or server. The sample still installs the Langfuse Python SDK.

A **trace** records the model requests, tool calls and results that led to an outcome. Use
one when a report tells you what failed but you need to inspect how the agent reached it.
Start with the local HTML report; add this integration when shared trace inspection would help.
[Design the evaluation review page](evaluation-results.md#design-the-evaluation-review-page)
explains how to group results, compare runs, and begin investigating before opening a trace.
The [inspection appendix](../reference/inspection.md) describes an example mapping between
application capabilities, offered tools, and execution records. Adapt it to your tracing system.

You can run Langfuse on your own computer using its
[Docker Compose setup](https://langfuse.com/self-hosting/deployment/docker-compose),
without a cloud subscription. Follow that guide to start it, then create a local account
and project at `http://localhost:3000`. For the todo app, set
`LANGFUSE_BASE_URL=http://localhost:3000` and use that project's API keys below.

You can instead use an existing Langfuse server or a
[Langfuse Cloud project](https://langfuse.com/cloud).
Create project API keys in that project's settings, and put the three values in this
repository's `.env` (never commit the file):

```dotenv
LANGFUSE_PUBLIC_KEY=your-project-public-key
LANGFUSE_SECRET_KEY=your-project-secret-key
LANGFUSE_BASE_URL=https://your-langfuse-host
```

Use the base URL for your own region or deployment. See
[Langfuse's setup guide](https://langfuse.com/docs/observability/get-started) for account setup.
Containers are needed only if you choose the local Docker Compose setup.

To watch personas without exporting anything, set `EVALBASICS_PERSONA_PLAYER=true` and
leave `LANGFUSE_TRACING_ENABLED=false`. The visible player and trace export are independent.

## With this app

- **Fixed evals:** `LANGFUSE_TRACING_ENABLED=true .venv/bin/python -m evaluations.evals --case read-fresh --repeat 1`.
  The runner sends synthetic cases and scores as an experiment and saves local records too.
  Cases are passed directly from code; you do not need to create a hosted dataset first.
- **Personas without the interface (headless):** `.venv/bin/python -m evaluations.personas --persona sam --turns 3 --trace`.
  These are exploratory sessions, separate from fixed-suite results.
- **Visible player:** `LANGFUSE_TRACING_ENABLED=true .venv/bin/python -m streamlit run todo/app.py --server.address 127.0.0.1`.
  Persona and exploratory-tester sessions may be exported. The screen identifies recording.
  Ordinary application chats are excluded by the export filter.

All three commands can incur model-provider charges. Without `--trace`, the headless
persona runner saves local records without exporting traces. For evals, set `LANGFUSE_TRACING_ENABLED=false` to disable
export even when project keys are configured. Opening a local HTML report makes no model calls.

An unavailable Langfuse server disables tracing without changing the application or its
graders. If a trace link is absent, first check the run's `tracing_enabled` field and the
startup message. Verify the host URL and project keys privately; do not paste credentials
into bug reports. The example sends queued traces before exiting.

The SDK is pinned in `requirements.txt` for repeatable examples. When upgrading, check both
local records and export behavior. For SDK details, see
[experiments using local data](https://langfuse.com/docs/evaluation/experiments/experiments-via-sdk).
