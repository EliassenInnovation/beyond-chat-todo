# A request through the todo app

This sample shows how a person's controls and an embedded agent use the same application operations. Follow a request from its entry point to validation, saved state, feedback, and undo. The model chooses an operation; application code decides whether that caller may run it and what actually changes.

Use this alongside the [reference review](sample-assessment.md), which maps the implementation to all 62 checks in Beyond Chat 3.5. The sample demonstrates a useful subset, not a complete implementation of every check.

## Relate the sample to “doing the job with them”

The presentation's progression starts with two familiar forms of help. They are the comparison
points for what changes when an agent is integrated into the app. The sample demonstrates
levels 3–5 directly and offers a small composition example for level 6.

| Level | What the person gets | Connection to this sample |
| --- | --- | --- |
| 1. Mechanical help | Keywords, pattern matching or a search box lead to help pages. The person finds the instructions and does the work. | The familiar starting point for comparison. |
| 2. Mechanical, with AI in front | AI helps find relevant information in the same help pages. The person still translates that help into actions in the app. | Better help retrieval alone does not give the assistant current UI state or control of the app. |
| 3. Tell me how | Directions in the app's own language, tied to its controls. | Ask “How do I hide completed tasks?” The reply names **Active** beneath the list and leaves the filter unchanged. |
| 4. Show me how | The assistant points at the control on the person's screen. | Ask “Show me where to do that.” **Active** is highlighted; the tasks and filter stay unchanged. |
| 5. Do it for me | The assistant performs the requested operation and confirms what changed. | Ask “Do it for me.” The filter changes to **Active**, the person sees the result, and the reply describes it accurately. |
| 6. Do something new for me | Existing operations are combined for a request that has no dedicated workflow. | Try the composition example below on a scratch list and inspect each outcome. |

The departure from levels 1–2 is the connection to the working application. The assistant can
use its current state, speak in the names of its controls, point to those controls and carry
out authorized actions. The person can move from explanation to demonstration to execution
within the same conversation.

The assistant receives the app's control names and locations, plus current list and view state.
Its screen actions use the same shared operations as the person's controls. This is why both
knowing what the person sees and being able to control the UI matter.

Level 6, “do something new for me,” can be explored by combining existing operations. On a
scratch list with distinct due dates, try “Show my unfinished tasks due this week, and move the
earliest one to the top.” There is no dedicated button for that combined request: the agent
must interpret the criteria, select tasks, change the view and reorder the chosen task. If no
tasks qualify or the choice is ambiguous, an appropriate response may be an explanation or a
question. Check that hidden tasks remain stored and unrelated tasks keep their relative order.

That last example is an exploration prompt, not a validated reliability claim or a new built-in
workflow. The sample supplies composable operations; evaluations measure whether a chosen model
uses them correctly.

## Start without a model or credentials

From the repository root, run:

```bash
python3 -m todo.walkthrough
```

Python 3.11 or later is enough. The script uses the real capability registry and domain code with a disposable list, checks each outcome, and removes its data on exit. It does not simulate a language model or claim to test one.

For the full app and tests:

```bash
./setup.sh
.venv/bin/python -m pytest -q
.venv/bin/python -m streamlit run todo/app.py --server.address 127.0.0.1
```

The list works without a provider key. Chat requires `OPENAI_API_KEY` in this repository's `.env` or the process environment. Chat sends the conversation and current list to the model provider and incurs API charges. Langfuse is optional and separate: ordinary app chats are not exported there. Use synthetic tasks for this walkthrough.

## Follow an addition

In the app, type a task in **What needs to be done?** and press Enter. With chat configured, ask the assistant to add another task. The language model's wording and choice of calls can vary; inspect the saved result rather than expecting an exact transcript.

Both paths arrive at the same declaration:

```text
Person's control → todo_view.apply → capabilities.execute
Model tool call  → Agent.run_tool  → capabilities.execute
                                      ↓
                              todos.add_todo
                                      ↓
                              TodoList transaction
                                      ↓
                               saved JSON file
```

Read [todo_view.apply](../../todo/todo_view.py), [Agent.run_tool](../../todo/agent.py), and [execute](../../todo/capabilities.py). The screen translates a component event into an action ID and arguments. The agent translates a tool name into the same action ID. Neither adapter implements adding a task.

This is central dispatch: both entry points reach the same operation and validation. The shared
`View` below holds the small amount of presentation state this app needs. The sample does not
implement a general UI state machine for navigation or multi-step workflows.

The declaration on `add_todo` in [todos.py](../../todo/todos.py) supplies the description, parameters, effects, and policy. `execute` checks the caller and arguments before invoking it. A batch validates every item before changing any, then commits once. The tool's returned receipt comes from application code.

The current agent still asks the model to repeat that receipt. This is a known gap against Check 4.4: producing reliable text in code is useful, but asking a model to reproduce it does not guarantee delivery. The evaluation checks repetition; a future change should render the receipt directly and evaluate the model's surrounding explanation separately.

Relevant checks: 1.1–1.3, 3.1, 4.4.

## Check the proposed change before executing it

Optional semantic guards sit in `Agent.run_tool`, after argument validation and before
`execute`. Each action names its guards; each guard declares its question, evidence, provider,
and refusal. The existing merge check and the newer target/action checks use the same dispatch.

[guard_check.py](../../todo/guard_check.py) groups checks that need the same evidence and runs independent
groups concurrently. The input check cannot see the model's proposed selection; the output
checks need it. Application code supplies calendar facts and the meanings of operations.
Answers are cached by their exact evidence, so changing an argument or a task forces a new check.
The agent checks for a changed list again after the remote calls, before executing the action.
Each check concerns the proposed operation, which may fulfill only part of a larger request.
Completeness of the whole request belongs to the conversation eval, not to each individual call.

A guard can be wrong. The experiment found that “appointment call” can still be mistaken for a
unique reference when more than one call could involve an appointment. A conversation eval
also caught a wrong date introduced by the assistant and accepted after the user clarified
which task they meant. These checks supplement
the deterministic protections; they do not establish that a request is safe or authorized.
See [model configuration](models.md) to enable them. The default configuration retains the
existing merge guard; the additional checks require explicit configuration.

## Separate the screen from saved data

The agent needs both observation and control. At the start of every turn, its current read
includes the active filter and visible task IDs, calculated from the shared `View`. It also
receives the screen's control descriptions. These describe application state, not a screenshot
or which pixels are inside the browser viewport. Hidden tasks remain available as data; they
are not mistaken for tasks the person can currently see.

Ask to show only unfinished tasks, or use **Active** below the list. Both paths call `view.show`. It changes the shared [View](../../todo/view.py), not the stored tasks. The offline walkthrough shows only one task and verifies that the saved file remains byte-for-byte unchanged.

For the language distinction, try “How do I hide completed tasks?”, then “Show me where”, then “Do it.” The intended outcomes are directions, a highlighted control, and a changed filter. The offline script proves the operations differ; paid evaluation is needed to measure how reliably the model chooses among them.

Relevant checks: 1.5, 1.13, 2.5.

## Request a deletion and inspect authority

Deletion is gated here to demonstrate an approval mechanism, not because deleting an ordinary
todo is inherently high-impact. The sample also makes deletion irreversible. Both are teaching
choices, not requirements to copy into another app. A real todo app could provide recoverable
deletion and reserve approval for more consequential actions.

Separate two questions when adapting this pattern: **does the mechanism enforce authority?**
And **do this action's consequences and recoverability justify approval?** The walkthrough tests
the first; the second is a product decision. Match safeguards to consequences rather than gating
every write.

Ask the assistant to delete a named task. It calls the `request_delete` tool, which resolves to the `todos.delete` action. For the agent, that action's policy is `approval`, so `execute` runs its proposal function. The task remains, and an Approve/Deny card appears.

Typing “approved” in chat cannot approve it. Even a direct call to `todos.approve` with `actor='agent'` is refused. The offline walkthrough attempts that bypass and checks that the task remains. Only the UI adapter establishes `actor='person'`; actor identity is not a model-supplied argument.

Click **Deny** and the task stays. A fresh request followed by **Approve** deletes it. Deletion is intentionally irreversible in this sample and clears older undo history; this is a design choice, not a requirement of the principles.

Approval applies to the requested task details. Rename the task, change its date, or mark it done after the request: approving the old request is refused. Deny it and request deletion again. Legacy saved requests without bound details also require renewal. These paths are covered by `test_approval_is_bound_to_requested_details_after_reload` and `test_legacy_approval_without_snapshot_requires_new_request` in [tests/test_reference.py](../../tests/test_reference.py).

Relevant checks: 3.3, 3.4, 3.9.

## Fail a batch without leaving half of it saved

The offline walkthrough asks to complete one existing task and one nonexistent task in the same action. Validation refuses the whole batch; neither the file nor the existing task changes.

A more important test fails the actual file replacement after a multi-item addition has executed in memory:

```bash
.venv/bin/python -m pytest -q tests/test_reference.py -k 'failed_batch or batch_commits'
```

`TodoList.transaction` restores the in-memory state when the operation or save raises. `save` writes a temporary file beside the destination, flushes it, and replaces the destination only when the write is complete. A UI change and its undo entry share that transaction. This demonstrates an atomic registered action under the tested failures; it does not turn the JSON file into a concurrent database or establish durability under every power-loss condition.

Relevant checks: 1.2, 3.1, 3.2.

## Recover when the model stops after saving

A request can save a task successfully and then lose the model service while asking for the final reply. The saved task must not vanish, and the app must not imply that nothing happened.

```bash
.venv/bin/python -m pytest -q tests/test_reference.py -k provider_failure
```

The test substitutes a model that first requests an addition and then raises a provider error. The agent returns a code-written interruption message with the saved action receipt, retains that reply in conversation history, and records an undo entry. The person's Undo button then removes the addition.

This is distinct from losing the response to the write itself. The sample has no durable operation IDs or replay receipts: repeating an addition after an uncertain response may add a duplicate. It therefore does **not** meet Check 3.10. Do not retry writes automatically when adapting it to a network service; implement operation identity and recovery first.

Relevant checks: 3.2, 3.10, 4.3.

## Read an evaluation as evidence

The [evaluation definitions](../../evaluations/evals.py) give each case a question, starting state, steps, expected outcome, and grading rules. Each attempt starts on a new temporary list. Code checks state; separate judges assess claims and answers. [tests/test_main.py](../../tests/test_main.py) exercises graders on both correct and incorrect outcomes.

With a configured model, these commands make paid API calls:

```bash
.venv/bin/python -m evaluations.evals --case read-fresh --repeat 3
.venv/bin/python -m evaluations.evals --repeat 3
```

The second command runs the visible suite. Held-out cases require an explicit case name and `--held-out`; do not inspect or run them while developing a fix. A configured Langfuse project receives synthetic evaluation traces; without it, local run reports remain available.

Open the generated `runs/evals.html`. Start with a case's question, expand an attempt, and compare the actual state and tool results with the reply. Follow the trace link when available for the full model request. Sample passing cases too.

A missing judge is missing evidence. All required truthfulness checks must return before an attempt can pass. A known failed check remains a failure even if another check is missing. Run records retain individual check verdicts and reasons; incomplete attempts must not inflate a pass rate.

These tests demonstrate that reporting rule without a model call:

```bash
.venv/bin/python -m pytest -q tests/test_reference.py -k 'judge or held_out'
```

Relevant checks: 6.1, 6.2, 6.6–6.10, 6.13.

## What to carry into another application

Keep the shared owner of each operation, execution-time permission checks, validation before mutation, truthful results, and tests for failures as well as successes. Replace the domain and storage. Keep the model's tool descriptions tied to the operations they describe.

Before a public or multi-user deployment, address the gaps in the [review](sample-assessment.md): concurrent storage, durable retries, cancellation, production audit records, directly rendered receipts, budgets, and release evidence. None requires adding an MCP server to this sample merely to demonstrate the architecture.

## Review reliability and explore new jobs

Use the [evaluation report guide](evaluation-results.md) to distinguish complete evidence,
unusual variation, and acceptable performance. A five-run pilot helps inspect failures
and cost; it does not establish statistical control.

Keep the visible persona player for watching the experience. For unattended exploration,
run `python -m evaluations.personas --persona sam --turns 3 --max-tokens 50000` using the project’s
virtual environment. Review the saved HTML beside its JSON record, then decide whether
a candidate finding should become a regression case. Persona findings do not enter the
fixed-suite control chart. The [README](../../README.md#watch-personas-or-run-them-unattended)
explains limits and offline replay. [Langfuse tracing](langfuse.md) is optional.
