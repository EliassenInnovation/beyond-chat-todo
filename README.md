# Build better agents

Principles, a working example, and evaluation tools from Eliassen Innovations to help you
build or improve an agent inside your application or website.

People come to your application to get something done. An embedded agent can help them find
an unfamiliar capability, understand what they are seeing, and carry out work with them.
A poor one can change the wrong thing or make claims the application cannot support.
This project shows how to build useful assistance and examine whether it works.

**[Read the complete illustrated guide](https://eliasseninnovation.github.io/beyond-chat-todo/guide/)** —
from motivation and architecture through the working implementation, model choices and evaluation.
You can also [read it as Markdown](docs/index.md) or [run it locally](#read-the-guide-locally).

[<img src="docs/images/guide-cover-thumbnail.png" alt="Cover of the guide: Build better agents. Help your users get things done." width="220">](https://eliasseninnovation.github.io/beyond-chat-todo/guide/)

## Contents

- [What the sample demonstrates](#help-people-get-the-job-done)
- [Configure a provider and run the app](#setup)
- [Test and explore](#test)
- [View recorded evaluation results](#read-the-report)
- [Follow the implementation](#follow-the-implementation)

## Help people get the job done

![From finding help to doing the job with the person.](docs/images/assistance-levels.svg)

Search and AI-assisted help point people to instructions. An embedded agent can also know
the current application state, point to a control, and perform an authorized operation.
The [guide](docs/guide/why.md) explains where that difference matters.

The familiar [TodoMVC](https://todomvc.com/)-style list keeps the example small enough to inspect.
It demonstrates **one implementation of each capability, shared by the UI and agent**, with
permissions appropriate to each caller. The destination is your application; todo management
is simply a teaching domain.

![The todo application with its embedded assistant and exploratory tester.](docs/images/exploratory-tester.png)

**Todo deletion stands in for an irreversible action.** Its approval gate demonstrates how
application code can require a person's approval for consequential actions the application
cannot undo, such as transferring money, placing a trade, or deleting a repository.
It is a teaching choice independent of how capable undo is; ordinary todo deletion would
rarely warrant it. [Follow the approval mechanism](docs/guides/walkthrough.md#request-a-deletion-and-inspect-authority).

## Setup

Python 3.11 or later is required. From a cloned repository:

```bash
./setup.sh
```

Setup creates `.env` from `.env.example` if it is absent. Choose **one** provider and add its
key in that file; the profile selects models for the application, guards and evaluation roles.

```dotenv
# OpenAI
EVALBASICS_PROVIDER=openai
OPENAI_API_KEY=your-key-here
```

Or:

```dotenv
# Anthropic
EVALBASICS_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
```

```bash
.venv/bin/python -m streamlit run todo/app.py --server.address 127.0.0.1
```

The list works without a key. The live assistant, evaluations, and personas send
conversation and list data to the selected provider using your key, and you are
responsible for those charges. We suggest you follow your model provider's practices for
setting limits on spending.
Use synthetic tasks when exploring. Keep `.env` private.
[Model configuration and tested choices](docs/guides/models.md) are in the guide.
Langfuse is optional; [its short setup chapter](docs/guides/langfuse.md) covers this sample's integration.

To inspect the real shared operations without installing dependencies or calling a model:

```bash
python3 -m todo.walkthrough
```

## Test

```bash
.venv/bin/pytest  # offline tests; no model calls
.venv/bin/python -m evaluations.evals --case read-fresh --repeat 3 --max-tokens 50000
```

The second command makes paid calls. A token allowance is not a hard dollar billing cap.
The guide explains [evaluation](docs/guide/evaluation.md),
[evidence completeness and control charts](docs/guides/evaluation-results.md), and how much testing a change needs.

## Watch personas or run them unattended

People exploring an app may repeatedly test the same kinds of requests. Simulated users broaden the requests
and reactions you can inspect. Watch them in the app or run them headlessly, then review
flagged findings and sample apparent successes. Neither persona satisfaction nor a smooth
conversation proves the application worked. [Run and review personas](docs/guide/exploration.md).

## Read the report

**[Open the evaluation report](https://eliasseninnovation.github.io/beyond-chat-todo/)** without a key,
account, or running Langfuse server. It contains 20 real historical runs and selected conversations.
Its candidate control limits are illustrative, not an accepted quality baseline; original
grading concerns remain visible. [Understand what it measures](examples/evaluation-review/README.md).

## Read the guide locally

The guide, including its interactive checklist builder, runs from a clone with no API key:

```bash
./preview.sh
```

Then open <http://127.0.0.1:8000/guide/>. The first run creates an isolated documentation
environment (Python 3 and an internet connection to install packages). Stop it with Ctrl-C.
Serve it this way rather than opening the built HTML files directly: the checklist builder
loads its data over HTTP, which browsers block for files opened from disk. On GitHub, the
builder appears only as plain Markdown. [Build and maintain the guide](docs/BUILDING.md) covers
editing and releases; a fork publishes under its own address when its release workflow runs.

## Follow the implementation

[Follow a request through the app](docs/guides/walkthrough.md), then
[apply the approach to your own application](docs/guide/apply.md).

| Folder | Purpose |
| --- | --- |
| `todo/` | Application, shared capabilities, guards and UI |
| `evaluations/` | Fixed cases, judges, personas and reports |
| `tests/` | Offline regression tests |
| `docs/` | The illustrated guide and detailed references |
| `examples/` | A self-contained evaluation report |

Run commands from the repository root. Local configuration is in `.env`, tasks in `todos.json`,
and new results in `runs/`; all are ignored by Git. This is a local, single-user teaching sample,
not a complete production architecture. [See its coverage and limitations](docs/guides/sample-assessment.md).

## License

The sample's original code and accompanying documentation are released under the [MIT License](LICENSE),
Copyright (c) 2026 Eliassen Group.
The styling in [todo_view.css](todo/assets/todo_view.css) is adapted from
[TodoMVC app CSS](https://github.com/tastejs/todomvc-app-css), copyright Sindre Sorhus,
under [CC BY 4.0](licenses/todomvc-app-css.txt). We changed its layout and sizing and added
styles for dates, approvals, undo, and other app controls. The TodoMVC attribution does not
imply endorsement of this sample.
