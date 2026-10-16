# Bring your own model

Choose models and supply your own provider credentials. The sample does not require one model
for every job, and its defaults are examples rather than recommendations. Model choice changes
how reliably the assistant interprets requests; application code still enforces permissions,
validation and approval.

## What you can configure today

| Job | Setting | Current API path | Required capability |
| --- | --- | --- | --- |
| Assistant in the app and fixed evals | `EVALBASICS_MODEL` | OpenAI-compatible Chat Completions | Function tool calls, tool-result messages, and ordinary text replies |
| Evaluation judges | `EVALBASICS_JUDGE_MODEL` | OpenAI-compatible Chat Completions, or native Anthropic when the name starts with `claude-` | Strict JSON-schema output; the Anthropic path uses a forced tool call |
| Merge intent guard, when enabled | `EVALBASICS_GUARDS`; model fixed by `GUARD_MODEL` in code | OpenAI Decisions API | Predicate decisions; chat compatibility alone is insufficient |
| Target/action guards | `EVALBASICS_GUARDS`, `EVALBASICS_ACTION_GUARD_MODEL` | OpenAI-compatible Chat Completions | Strict JSON-schema boolean answers |
| Simulated users, visible or headless | `EVALBASICS_PERSONA_MODEL` | OpenAI-compatible Chat Completions | Strict JSON-schema output |

“OpenAI-compatible” describes the request format, not a guarantee that every endpoint implements
all the features this app sends. The app's agent and personas do **not** currently have native
Anthropic, Gemini, Bedrock or Azure-specific adapters. Putting a native provider's model name in
an environment variable does not add one. A compatible gateway can expose another provider's
model, but that route needs verification against the requirements above.

The defaults are declared in [agent.py](../../todo/agent.py), [judge.py](../../evaluations/judge.py), and
[personas.py](../../evaluations/personas.py). Check the provider's current catalog and your account's access
before choosing a model; a historical run does not establish current availability.

## The merge guard

The existing merge guard asks a separate model whether the user identified which tasks to
merge. All declared guards are enabled by default. The launcher, direct Streamlit,
persona runner and eval runner use the same selection: `EVALBASICS_GUARDS` in the
environment takes precedence over this repo's `.env`, then the code default.
Setup does not overwrite existing `.env` files; update an older explicit selection
to match `.env.example`. An explicitly empty shell environment value disables guards.
`evals.py --guard NAME` adds a guard to the configured selection.

This guard uses `GUARD_MODEL` in `todo/agent.py` (currently `gpt-6-luna`) and the Decisions API,
not Chat Completions. A compatible chat endpoint alone is insufficient. It shares the
OpenAI key and base URL; there is no separate guard endpoint or environment model selector.
If the enabled guard cannot answer, the merge is refused. Guard calls are recorded in usage and priced separately at the documented input-only
Decisions rate. Include guard configuration
when comparing runs; the earlier guard-disabled prices do not price a guarded baseline.

## Checks of proposed changes

The completion, due-date, and deletion-request actions declare checks of user intent
and proposed actions. They use `EVALBASICS_ACTION_GUARD_MODEL` (default `gpt-6-luna`, with low
reasoning for GPT-5/6 models), independently of the assistant model. They use the existing
`OPENAI_API_KEY` and `OPENAI_BASE_URL`; no additional provider account is required.

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
adding a guard to another operation requires evaluation. The existing merge guard is unchanged.

An earlier omission question falsely blocked valid compound requests. Asking whether the user
requested this same operation on tasks missing from the action removed those refusals in
40 repeated conversations: all requested deletion approvals were created, versus 11 missing
before. This is development evidence, not a production failure-rate estimate. Ambiguous
descriptions can still pass, and a wrong date introduced earlier by the assistant can be
accepted after the user clarifies the task. The person can still use the controls; deterministic
deletion approval remains in place.
Computed weekdays help with calendar arithmetic; they do not prove that a date matches intent.

## Select models

Copy `.env.example` to `.env` if setup has not already done so. Replace these placeholders with
model IDs available to your account and a key for the chosen endpoint:

```dotenv
OPENAI_API_KEY=your-endpoint-api-key
EVALBASICS_MODEL=your-tool-capable-model-id
EVALBASICS_JUDGE_MODEL=your-structured-output-model-id
EVALBASICS_PERSONA_MODEL=your-structured-output-model-id
LANGFUSE_TRACING_ENABLED=false
```

Chat uses the assistant model and, for guarded merges, the guard model. Judges run during evaluation; personas run when
you use the persona player or headless runner. They may use the same model, but have different
requirements. No model credential is needed to use the list manually or run offline tests.

Restart the app or command after changing settings: model defaults are read when modules load,
and active agents retain their clients and conversation. Process environment variables take
precedence over `.env`; an old exported value can override your edit. This project's `.env` is
the only file loaded. Keep credentials out of source control.

### Use a compatible endpoint

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

**This setting is shared:** the assistant, non-Anthropic judges and personas all use the same
`OPENAI_BASE_URL` and `OPENAI_API_KEY` within a process. Select model IDs that endpoint serves
for every role you intend to run. Separate endpoints or keys per role require a code change;
there are no per-role endpoint settings today. The installed SDK's environment handling was
checked against its implementation and the [OpenAI Python SDK documentation](https://developers.openai.com/api/reference/python).

### Use a native Anthropic judge

The existing judge adapter selects Anthropic for a `claude-` model ID:

```dotenv
EVALBASICS_JUDGE_MODEL=claude-your-model-id
ANTHROPIC_API_KEY=your-anthropic-api-key
```

Replace the placeholder with an actual supported model ID. This changes the judge only. The
assistant and personas retain their OpenAI-compatible connection. It also means a gateway model
whose ID starts with `claude-` is routed to native Anthropic by the current judge code; there is
no explicit provider override. The native path is implemented, but this follow-up did not run a
live Anthropic evaluation or verify its Langfuse tracing. Local usage capture wraps both paths.

## Compatibility limits to check

- **Tool protocol:** the assistant expects OpenAI-style tool-call IDs, JSON argument strings,
  and matching tool-result messages. A text-only model is insufficient.
- **Structured results:** judges and personas require the schema contract; an endpoint that
  merely returns JSON text may not enforce it. Check refusals and truncated output as well as
  successful calls. An unavailable judgment must remain missing evidence, never a pass.
- **Generation options:** `agent.options()` currently sends `reasoning_effort='none'` for names
  starting with `gpt-5` or `gpt-6`. The OpenAI judge path sends `reasoning_effort='low'` for those
  prefixes and `temperature=0` otherwise. Personas use the agent options or `temperature=0.7`.
  These are code choices for the existing integrations, not universal model capabilities.
  A gateway alias or another model may require different options. If the endpoint rejects a
  parameter, adapt the client options against its documentation; there is no generic options
  environment variable today.
- **Standalone experiments:** `request_parts_experiment.py` and archived pilot wrappers pin
  their own models and cost assumptions. The three settings above do not override those scripts.

## Try a replacement and measure it

Start with a scratch list and trace export off. These first commands make no model calls until
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

## If you need another native API

Add a provider adapter at the model-call boundary for messages, tool calls, results, structured
output, errors and usage. Keep domain operations and authority in `capabilities.execute`; do
not reimplement todo actions for each provider. Agent, judge and persona paths need separate
verification. Native provider adapters and independent per-role endpoints are extension work,
not features claimed by the current starter.
