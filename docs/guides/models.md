# Bring your own model

Set your API key and model IDs in `.env`, then restart the app. This guide covers the settings,
provider requirements, and checks to make before relying on a replacement model.

[Select models](#select-models) · [Model costs](#model-costs) · [Use another endpoint](#use-a-compatible-endpoint) · [Check compatibility](#compatibility-limits-to-check) · [Test the change](#try-a-replacement-and-measure-it)

## Select models

Run `./setup.sh`, then edit `.env` in the repository root. Choose a provider and add its key:

```dotenv
EVALBASICS_PROVIDER=anthropic
ANTHROPIC_API_KEY=
```

Or use the OpenAI profile:

```dotenv
EVALBASICS_PROVIDER=openai
OPENAI_API_KEY=
```

Fill in the blank key for your choice. The [sample configuration](../../.env.example) supports
both providers; you need only one key. Leave the optional model overrides commented out to
use the profile defaults. If an older `.env` already sets model IDs, remove or comment those
lines before switching profiles; explicit overrides take precedence.

| Role | OpenAI profile | Anthropic profile |
| --- | --- | --- |
| Application agent | `gpt-6-luna` | `claude-haiku-5-5` |
| Evaluation judges | `gpt-6-luna` | `claude-sonnet-5-5` |
| Exploratory personas | `gpt-4.1-mini` | `claude-haiku-5-5` |
| Intent/action guards | `gpt-6-luna` | `claude-haiku-5-5` |
| Merge judgment | Decisions API probability | Structured boolean answer |

Both provider profiles use [guards](walkthrough.md#check-whether-the-proposed-action-fits-the-request) to check that
proposed actions match the user's intent before execution. These checks supplement application-enforced
permissions, validation, and approval. The Anthropic profile makes no OpenAI calls. Boolean guard
answers are not probabilities; changing provider or judgment mode starts a new evaluation
configuration. Both profiles have live development-run evidence. Switching providers still requires
evaluation for your application; supported transport does not establish equivalent behavior.

Restart the app or command after changing settings:

```bash
.venv/bin/python -m streamlit run todo/app.py --server.address 127.0.0.1
```

Try an addition and read it back. Chat and evaluation calls incur provider charges. The
manual list and offline tests need no key. Langfuse stays off in the sample configuration.

Process environment variables override `.env`, and setup preserves an existing `.env`.
Keep keys out of source control. Leave provider base URLs unset for the standard endpoints.

### Optional model and provider overrides

Set `EVALBASICS_MODEL`, `EVALBASICS_JUDGE_MODEL`, `EVALBASICS_PERSONA_MODEL`, or
`EVALBASICS_ACTION_GUARD_MODEL` to replace a role's model. The chosen provider must serve that
model. For a mixed setup, also set the corresponding provider override:
`EVALBASICS_AGENT_PROVIDER`, `EVALBASICS_JUDGE_PROVIDER`, `EVALBASICS_PERSONA_PROVIDER`, or
`EVALBASICS_ACTION_GUARD_PROVIDER`. Values are `openai`, `anthropic`, or `auto` (infer from a
`claude-` prefix). Without an explicit profile, the older prefix-inference behavior remains.

For example, to compare only the agent while keeping OpenAI judges and guards:

```dotenv
EVALBASICS_PROVIDER=openai
EVALBASICS_AGENT_PROVIDER=anthropic
EVALBASICS_MODEL=claude-haiku-5-5
```

That mixed configuration needs both keys. Judge and guard changes should be measured
separately from agent changes when you want to attribute a difference.

## Model costs

Model prices vary widely. Providers generally charge for input tokens (the instructions,
conversation, and application data sent to the model) and output tokens (its response,
including billable reasoning). One user request can involve several model calls, including
guards and follow-up calls after tools return results.

Budget separately for using the app and evaluating it. Evals add judge calls; persona runs
also pay for the simulated user. Repeated runs multiply those costs, and a more expensive
judge can cost more than the agent it evaluates. Choose models for each role using measured
quality, response time, and total cost—not price per token alone.

For current rates, caching discounts, and other billing details, see
[OpenAI API pricing](https://developers.openai.com/api/docs/pricing) and
[Anthropic API pricing](https://platform.claude.com/docs/en/about-claude/pricing).
The sample's recorded costs are estimates for particular configurations and workloads;
check your provider's usage dashboard for actual charges. Start with a small run before
budgeting for a larger evaluation. The [tested configuration](#what-we-tested) below gives
an example of how model choice affected this sample's grading costs.

## What you can configure today

| Job | Model setting | Required capability |
| --- | --- | --- |
| Application agent | `EVALBASICS_MODEL` | Tool calls and tool results |
| Evaluation judges | `EVALBASICS_JUDGE_MODEL` | Structured output |
| Simulated users | `EVALBASICS_PERSONA_MODEL` | Structured output |
| Boolean guards | `EVALBASICS_ACTION_GUARD_MODEL` | Structured boolean output |
| Probability merge guard | `GUARD_MODEL` in `todo/agent.py` | OpenAI Decisions API |

Defaults live in [model_provider.py](../../todo/model_provider.py). The native Claude adapter
uses [Messages tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)
and [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).
The OpenAI path uses Chat Completions and, for its default merge guard, Decisions.
Check model availability and account access before replacing a model.

## Use a compatible endpoint

Leave `OPENAI_BASE_URL` unset for the default OpenAI endpoint. For a gateway or local server,
set its documented API base URL, for example:

```dotenv
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=your-local-server-key
```

This is an illustrative address, not a server installed by this sample. Use the endpoint's
actual URL and authentication requirements. The SDK requires a nonempty key; use a placeholder
only if your own local endpoint explicitly does not authenticate. For a hosted endpoint, use
that provider's key. Requests and task data go to the configured endpoint.

`OPENAI_BASE_URL` and `OPENAI_API_KEY` apply to roles routed to OpenAI-compatible APIs.
`ANTHROPIC_BASE_URL` and `ANTHROPIC_API_KEY` apply to native Anthropic roles. Separate endpoints
within one provider require a code change. A gateway's Claude model can use the OpenAI-compatible
path with an explicit `openai` role override; a model name alone does not establish compatibility.

## The merge guard

The existing merge guard asks a separate model whether the user identified which tasks to
merge. All declared guards are enabled by default. The launcher, direct Streamlit,
persona runner and eval runner use the same selection: `EVALBASICS_GUARDS` in the
environment takes precedence over this repo's `.env`, then the code default.
Setup does not overwrite existing `.env` files; update an older explicit selection
to match `.env.example`. An explicitly empty shell environment value disables guards.
`evals.py --guard NAME` adds a guard to the configured selection.

With the OpenAI profile, this guard uses `GUARD_MODEL` in `todo/agent.py` (`gpt-6-luna`)
and the Decisions API. With the Anthropic profile, it uses the action-guard model and the
same question with a boolean answer. Neither path changes the application's approval rules.

`EVALBASICS_MERGE_GUARD_MODE` can explicitly select `decisions` or `boolean`. By default,
an Anthropic action-guard provider selects boolean; an OpenAI action-guard provider selects
Decisions. Boolean mode can also be evaluated with an OpenAI structured-output model.
The report records an answer or a probability according to the mode actually used. An invalid
or unavailable judgment prevents the merge. Include the mode and model in comparisons.

## Checks of proposed changes

The completion, due-date, and deletion-request actions declare checks of user intent
and proposed actions. They use `EVALBASICS_ACTION_GUARD_MODEL` and the action-guard provider, independently of
the assistant model. Both profiles use their own provider's key; no second account is needed.

These checks are enabled by default, alongside `todos.merge_unnamed`:

```text
todos.target_identified,todos.extra_tasks,todos.omitted_tasks,todos.operation_matches,todos.wrong_values
```

The input check receives dialogue through the latest user request, current tasks, and date.
It receives neither the proposed action nor the model’s narration of that proposal. The output checks also receive that action, tool meanings, and computed calendar
facts. Both requests run concurrently before a write. Each returns boolean answers, not
calibrated confidence scores. Date changes additionally check the proposed values.

Checks apply to one operation at a time: a request containing several operations need not
be completed by one call. The final-response eval checks completeness across the request.
A missing key, timeout, refusal, or invalid answer prevents that invocation; the assistant
receives an error and the person can still use the app's controls. Local tool records and
the HTML eval report include the answers; Langfuse is optional.

These are fallible semantic checks, not execution permissions. They do not replace validation,
current-state checks, deletion approval, or undo. They cover only the three measured operations;
adding a guard to another operation requires evaluation. The merge question remains separate and keeps its own evidence scope.

Check both false refusals and incorrect approvals when changing these models. Ambiguous
references and dates require particular attention. Computed weekdays help with calendar
arithmetic; they do not establish that a date matches the person's intent.

## Compatibility limits to check

- **Tool protocol:** the adapter must preserve call IDs, arguments, and matching results.
  The native Claude adapter retains thinking blocks and rejects truncated tool responses
  before execution. A text-only model is insufficient.
- **Structured results:** personas return their message plus approval choices, completion, and
  reactions as named fields; judges return a verdict and supporting quote. The
  [walkthrough explains the persona turn](walkthrough.md#how-a-persona-takes-a-turn). Both
  require the schema contract; an endpoint that
  merely returns JSON text may not enforce it. Check refusals and truncated output as well as
  successful calls. An unavailable judgment must remain missing evidence, never a pass.
- **Generation options:** `agent.options()` currently sends `reasoning_effort='none'` for names
  starting with `gpt-5` or `gpt-6`. The OpenAI judge path sends `reasoning_effort='low'` for those
  prefixes and `temperature=0` otherwise. Personas use the agent options or `temperature=0.7`.
  These are code choices for the existing integrations, not universal model capabilities.
  A gateway alias or another model may require different options. If the endpoint rejects a
  parameter, adapt the client options against its documentation; there is no generic options
  environment variable today.

## Try a replacement and measure it

Start with a separate test list and trace export off. These first commands make no model calls until
you send a chat message:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m streamlit run todo/app.py --server.address 127.0.0.1
```

Try adding a task, reading it back, changing a date, undoing a change, asking an ambiguous question,
and requesting deletion. Check both the resulting state and the explanation. Approval must
still be a person's action. Do not infer permission from a model's willingness to call a tool.

Next, run a small visible eval before paying for the full suite:

```bash
.venv/bin/python -m evaluations.evals --case read-fresh --repeat 1 --max-tokens 50000
.venv/bin/python -m evaluations.evals --repeat 3 --max-tokens 2000000
```

These commands incur charges at your provider. Token allowances are stop conditions between
calls, not dollar caps; an in-flight call can exceed the allowance. Inspect the JSON/HTML record
for provider errors, missing judgments and token usage, not just passes. A small smoke test
checks the connection; the full visible suite checks wider behavior. Do not use held-out cases
while adapting the integration.

When comparing assistant models, keep the judge, cases, tool order and other settings fixed.
Changing the judge at the same time changes the measuring instrument. Review a judge against
labelled examples before trusting its scores; a different model family can be useful but is not
automatically a better judge. The existing calibration command makes paid calls:

```bash
.venv/bin/python -m evaluations.judge_calibration --repeat 3
```

New model or endpoint configurations start a new comparison period. Local fixed-eval records
retain requested/served model evidence and hashes of endpoint settings without saving the
endpoint URL or credentials in the configuration fingerprint. Do not pool results across
configurations into an existing control baseline. See [evaluation signals](evaluation-results.md).

## Costs and optional tracing

The local estimator in [eval_costs.py](../../evaluations/eval_costs.py) recognizes a small set of model IDs and
rates. An unfamiliar model or usage format produces an unknown estimate, not a free run. A
compatible provider reusing a recognized model ID may charge different rates; the current
estimator does not distinguish provider prices. Use your provider's billing as authoritative,
and update/test the estimator before using its numbers to plan a new provider's budget.

Langfuse is optional and does not select or host your model. Verify tracing compatibility for
any new provider separately from task behavior. Local records remain the primary evidence;
see the app-specific [Langfuse guide](langfuse.md).

## Conversational LLMs and decision models

A conversational LLM can interpret a request, propose tool calls, and explain results. A
purpose-built decision model answers narrower questions for application code, such as
“Has the user uniquely identified a task?” Its interface returns typed answers, often with
probabilities, rather than a conversational reply. [Jev](https://docs.typesafe.ai/introduction.md)
is one example.

An LLM can also answer a narrow question using structured output. That makes it usable as
a decision step; it does not make a yes/no answer a calibrated probability. The distinction
here is the job and interface, not a claim that the underlying model technologies cannot overlap.

The OpenAI profile uses a probability-returning Decisions call for the merge guard and
structured boolean answers for the other guards. The Anthropic profile uses structured
boolean answers for all guards. It does not claim that Claude supplies a separate decision
model or that a boolean is a calibrated probability. Jev is not integrated into this sample.

With either approach, model judgments remain fallible. Application code enforces permissions,
validates arguments, and requires deletion approval.

## If you need another native API

Add a provider adapter at the model-call boundary for messages, tool calls, results, structured
output, errors and usage. Keep domain operations and authority in `capabilities.execute`; do
not reimplement todo actions for each provider. Agent, judge, guard and persona paths need separate
verification. OpenAI-compatible and native Anthropic paths are implemented; other native APIs
and independent endpoints within one provider remain extension work.


## What we tested

The Anthropic profile uses **Haiku 5.5 for the application, guards, and personas**, and
**Sonnet 5.5 for evaluation judges**. A model that works well as the agent is not automatically
the best evaluator. You can override the judge with `EVALBASICS_JUDGE_MODEL`.

We selected Sonnet after comparing Haiku, Sonnet, and Opus against 206 calibration examples,
with three judgments per example. Haiku agreed with 607/618 labels at its default effort;
increasing its effort still produced errors in focused checks. Sonnet initially missed a
claimed return that had not happened. Clarifying that a return implies a state change brought
Sonnet to **618/618** across the full set. Opus also matched **618/618** in the initial comparison.
No labels were changed during this model comparison.

Regrading the same 51 saved application conversations cost an estimated **$0.88 with Sonnet**,
compared with **$1.74 with Opus**, using reported tokens and standard rates. Both passed 51/51.
These are judge costs, excluding agent and persona calls; actual charges and usage vary.
Sonnet uses the provider's default effort. Opus remains an optional override, not a required
part of the sample.

Validation on October 16, 2026:

- **312 offline tests passed**, including provider isolation, tool history, recovery, and cost accounting.
- The latest full application run passed **51/51 visible cases**. Rechecking its saved
  conversations with Sonnet also passed **51/51**, without missing judgments or replacing the originals.
- The final Sonnet rubric matched **618/618 calibration judgments** (206 examples, three times
  each), including correct and incorrect replies. These are repeated development checks,
  not 618 independent examples or a guarantee of accuracy on new requests.

The reviewed criteria separate truthfulness from task completion: “back below” can truthfully
name a relative position without restoring the original slot. The outcome check must still
reject the wrong slot. Showing all active tasks, including overdue ones, does not by itself
address “overdue first”; the response needs to identify, highlight, filter to, or ask about
the overdue tasks.

Before this model comparison, two labels were reviewed with the maintainer and changed;
an identical duplicate was updated consistently. Other calibration labels were initially
assigned by a coding agent, so agreement is development evidence, not independent proof of
judge accuracy. Review disagreements and sample apparent successes. Silence-related cases
also exercise the same deterministic check used by application evaluations.

Real browser chat and all five exploratory personas have also been exercised. Persona
satisfaction is exploratory feedback, not a pass score. Application code delivers action
confirmations directly; the model's additional explanation remains separately assessed.

Changing the judge starts a new comparison period. Retain earlier results and never merge
new grades into old control limits. Tracing was disabled for these checks: native usage is
recorded locally, but exported Anthropic traces have not been verified against a running
Langfuse instance.
