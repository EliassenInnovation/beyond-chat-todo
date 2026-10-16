# Beyond Chat Todo

An Eliassen Innovations sample: a working todo app with an embedded agent, shared application operations, and evaluations.
Use it to follow a request from a screen control or model tool call through permission checks,
validation, saving, feedback, and undo. Langfuse provides optional tracing and an experiment viewer.

The central pattern is **one implementation of each operation, shared by the person and the agent**.
The code enforces permissions; evaluations measure whether the agent chooses and explains the right work.

The UI is deliberately small, but demonstrates two requirements: the agent knows what the
person sees and can control the view. Each turn receives the task list, active filter and
visible task IDs. Screen actions change filters, show selected tasks or highlight controls
through the same central dispatch as the person's controls. A larger application may also
need an explicit UI state machine for navigation and multi-step workflows.

The [walkthrough](docs/guides/walkthrough.md#relate-the-sample-to-doing-the-job-with-them) follows the
presentation's six levels. It starts with familiar keyword help and AI-assisted help retrieval,
where the person still does the work. The sample shows the next steps: **tell me how → show me
how → do it for me**, using the app's current state and controls. It also includes a small
example of combining operations for a request without a dedicated button.

## Start here

The [documentation index](docs/README.md) points to practical guides and the principles documents.

The accompanying documents explain the approach:

- [Design principles](docs/principles/principles.md): why the architecture is structured this way.
- [Implementation guide](docs/principles/implementation.md): quick checklist, contracts, and acceptance checks.
- [Evaluating agents](docs/principles/evaluating-agents.md): how to measure and review behavior.


Read the [walkthrough](docs/guides/walkthrough.md), or run its shared-action examples without
installing anything or providing credentials:

```bash
python3 -m todo.walkthrough
```

The [reference review](docs/guides/sample-assessment.md) maps the sample to all 62 checks in
Beyond Chat 3.5, identifies the tested behavior, and lists the remaining gaps. This is a
local single-user sample; the JSON store is not a multi-user database.

## Why deletion requires approval here

The agent must request approval before deleting a todo to demonstrate how application code
enforces authority. This is a teaching choice, not a recommendation to require approval for
ordinary todo deletion. Deletion also cannot be undone in this sample; that limitation is not
inherent to todo apps.

When adapting the sample, match safeguards to consequences and recoverability. Low-impact
changes may need only visible results and reliable undo. High-impact or irreversible actions
may warrant explicit approval of the specific proposed change, with the boundary enforced in
code. Requiring approval for every write would add friction without necessarily adding value.

The sample's tests establish that the agent cannot approve its own request and that approval
applies to the proposed task details. Whether an action should require approval is a separate
product decision. See the [deletion walkthrough](docs/guides/walkthrough.md#request-a-deletion-and-inspect-authority).

## Setup

Python 3.11 or later is required.

```bash
./setup.sh
.venv/bin/python -m streamlit run todo/app.py --server.address 127.0.0.1
```

Setup installs the dependencies and creates `.env` from `.env.example` if absent. It does
not edit shell profiles or access a credential vault. The list works without API keys.
For chat and paid evaluations, set `OPENAI_API_KEY` in this repo's `.env` or environment.
Conversation and list data are sent to the model provider when you use chat. The example
configuration enables intent and action guards for completion, dates, deletion requests,
and unnamed merges. The merge guard requires the Decisions API; the other checks use
strict JSON-schema chat responses. Existing installations should copy the
`EVALBASICS_GUARDS` selection from `.env.example` if they already specify a smaller set.
See the model guide for configuration and provider compatibility.

Langfuse is optional. Configure this project's own keys if you want synthetic evaluation
or persona traces; no credentials are borrowed from other repositories. Ordinary app chats
are not exported to Langfuse.

For model selection, provider compatibility, credentials and comparison runs, see
[Bring your own model](docs/guides/models.md).

For this app’s optional tracing setup, see [Langfuse integration](docs/guides/langfuse.md).
For evidence completeness, run history, control limits, and acceptance criteria, see
[reading evaluation results](docs/guides/evaluation-results.md).

## Test

```bash
.venv/bin/pytest                          # the app, the agent's permissions, every grader; no model calls
.venv/bin/python -m evaluations.evals --max-tokens 2000000  # visible cases x 3; paid calls with a token allowance
.venv/bin/python -m evaluations.evals --case read-fresh --repeat 5
```

Each case runs several times, because a model does not answer the same way twice; the report
is a pass rate. Code checks saved outcomes; model judges check claims, abilities, approvals, and whether
each request received an answer. A code check verifies the application receipts. Missing
required judgments make an attempt inconclusive, never a pass.
Failed attempts, crashes included, print with their conversation, so the report can be read
without Langfuse; with Langfuse, each links to its trace.

## Watch personas or run them unattended

Set `EVALBASICS_PERSONA_PLAYER=true` in `.env` to show the visible player without enabling
trace export (the sample configuration includes it). It lets you watch a persona interact
with the actual screen. Pick a persona, then use Next or Play to watch. Each persona
uses a scratch list; pick None to return to your own list. The command-line runner uses the same persona prompts,
screen description, and approval actions, with a separate scratch list for each session:

```bash
.venv/bin/python -m evaluations.personas --persona sam --turns 8 --max-tokens 50000
.venv/bin/python -m evaluations.personas --replay runs/personas/RECORD.json
```

The first command makes paid calls for the persona, application agent, and claim judge.
It saves JSON checkpoints throughout the conversation and creates a standalone HTML review
beside the record. The second command regenerates that review without making model calls.
Use Previous/Next to inspect the recorded conversation, approval clicks, and state changes.
It does not rerun actions or reproduce the visual interface. Older persona JSON records
can also be reviewed; evidence they did not record is identified as missing.

`--max-tokens` is shared across all selected personas and all three model roles.
It stops further calls after reported usage reaches the allowance;
a call already underway can exceed it. Missing usage stops further calls too. This is
**not a hard dollar billing cap**; provider retries and charges without returned usage may
not be measurable locally. Choose a small turn limit for an initial exploration.
Ctrl-C retains the latest checkpoint. A record left with status `running` after a forceful
termination is incomplete, not a successful session.

Langfuse is an optional example integration, not a requirement or recommendation over other
tools. Headless exploration exports no traces unless you add `--trace` and configure your
own project keys. Local records and HTML review work without a Langfuse account or server.
The Python dependencies still include its SDK. Ordinary application chats are not exported.

Persona frustration and judge warnings are **candidate findings for human review**, not
fixed-suite failures. Review the conversation, decide whether it exposes a real problem,
then add a regression case and a separate held-out variant. Do not mix exploratory persona
sessions into the fixed-suite control chart. Headless exploration does not verify rendering,
layout, or interaction through actual browser controls; the visible player remains valuable.

## Read the report

You can inspect a completed example before setting up any model or tracing service:
open [the offline evaluation review](examples/evaluation-review/index.html). It contains
20 real runs, an illustrative chart, and a short human-review queue. Its original grades
and unresolved grading concerns are visible; candidate limits are not presented as an
accepted quality baseline. The page makes no network or model calls.

A full evaluation creates `runs/evals.html`. Open it in a browser, or regenerate a report
without making model calls:

```bash
.venv/bin/python -m evaluations.evals_page runs/RECORD.json
```

The page starts with results, then separates evidence completeness, unusual variation,
and acceptance criteria. Open a case and an attempt to inspect the conversation and saved
outcome. Trace links are optional. See [reading evaluation results](docs/guides/evaluation-results.md)
for everyday checks versus baseline collection, what happens to control limits when code
changes, cost estimates, and explicit acceptance rules. Twenty full runs are a baseline-building
exercise, not a requirement after every edit.

## Follow the implementation

The repository is organized by purpose:

- **todo/** — the application, shared capabilities, guards, and UI assets.
- **evaluations/** — evals, model judges, persona runner, report tools, and grading fixtures.
- **tests/** — offline regression tests.
- **docs/** — the principles, walkthrough, model configuration, and evaluation guidance.
- **examples/** — a self-contained evaluation report you can open without setup.

Run commands from the repository root. Local configuration stays in `.env`; saved tasks
stay in `todos.json`, and new evaluation records go in `runs/`. These are ignored by Git.


| File | Responsibility |
| --- | --- |
| `todo/capabilities.py` | Shared action declarations and execution policy |
| `todo/todos.py` / `todo/view.py` | Saved tasks and screen state |
| `todo/agent.py` / `todo/app.py` | Model interaction and visible application |
| `evaluations/evals.py` / `evaluations/judge.py` | Fixed cases and code/model checks |
| `todo/model_usage.py` / `evaluations/run_evidence.py` | Local usage and configuration evidence |
| `evaluations/eval_monitor.py` / `evaluations/evals_page.py` | Monitoring rules and local review |
| `evaluations/personas.py` / `evaluations/persona_report.py` | Exploration and offline session review |
| `todo/langfuse_setup.py` | Optional tracing configuration |

The app defaults to GPT-6 Luna for agent and judge calls, and GPT-4.1 mini for personas.
`EVALBASICS_MODEL`, `EVALBASICS_JUDGE_MODEL`, and `EVALBASICS_PERSONA_MODEL` select them; changing a judge requires
calibration, and changing a model starts a new comparison period. The historical persona
default is now [deprecated](https://developers.openai.com/api/docs/models/gpt-4.1-mini);
select a supported structured-output Chat Completions model when adapting the sample.


## What about Jev and other decisions models?

The todo app uses a narrow decisions-model guard before merging tasks: it checks whether
the user identified which tasks to merge. We have also used decisions models in other
contexts. Model checks also compare proposed completion, date, and deletion requests
with the user’s intent. We have used Jev in other contexts; this sample does not require it.
See [conversational LLMs and decision models](docs/guides/models.md#conversational-llms-and-decision-models) for the distinction, scope, limitations,
and provider requirements. These checks supplement the app’s validation and approval rules.

## License

The sample code and accompanying documentation are licensed under [MIT](LICENSE).
The license does not grant trademark rights in the Eliassen Innovations name or branding.
Historical presentation assets are not included.
