# Beyond Chat: Implementation Guide

**For development agents and the engineers who direct them**

Version 3.5-draft · October 15, 2026

> **Note:** Following these practices does not make an application secure. We have tried red teaming and prompt-injection tests, but encryption, transport security, authentication, and other standard security are outside this document's scope. Security for an application with an agent belongs to corporate governance, with policy and controls in place.

This guide turns [Beyond Chat: Building Agents into Applications](beyond-chat-building-agents-into-applications.md) into work a development agent can do and a reviewer can check. Read the principles first; this guide assumes their vocabulary and does not repeat their reasoning. It holds the acceptance checks (IDs are stable across versions), the proposed registry, observation and reference contracts, the evaluation infrastructure, and the rules for scoping a handoff. The [compact checklist](beyond-chat-agent-checklist.md) summarizes it for persistent context.

## Working with this guide

Use the principles to guide decisions in the codebase, alongside the project's own requirements and conventions. The examples illustrate the principles; they do not require any particular features, an MCP server, or the architecture of the applications the examples come from.

- **Inspect before proposing.** Trace a real request from an interface through validation, execution, saving, feedback, and recovery. Identify what is shared and what is duplicated.
- **Make gaps concrete.** For each relevant principle, distinguish implemented behavior, tested behavior, and missing behavior. Cite code or test evidence; a registry or a passing unit test alone does not prove an end-to-end guarantee.
- **Fix the shared owner.** Prefer changes to the capability or the shared execution path over special cases in individual interfaces. Keep display logic in the interface. Do not add prompt instructions to compensate for missing data or an inadequate tool description or result.
- **Stay within the task.** Apply the principles to the requested work and identify related gaps. This guide is not permission to build every interface, redesign the application, weaken policy, or perform consequential actions.
- **Verify the user's experience.** Exercise the real entry point, complete target selection, the saved result, feedback, and recovery, including failures and partial completion.
- **Report evidence and limits.** Say what changed, what was checked, and what remains unresolved, against the check IDs.

### Scope the handoff and the report

After reviewing and adapting the principles, assign a capability, interfaces, and check IDs: "Trace the reschedule capability through UI and CLI; report gaps against Checks 3.1–3.7. Do not change code." For implementation, name the permitted change. "Apply this document" is not a bounded task.

Report one row per relevant check and interface:

| Check | Interface | Result | Implemented | Tested | Missing |
| --- | --- | --- | --- | --- | --- |
| 3.1 | CLI | Fail | Save path and code location | Test command and observed failure | Partial-write rollback |

The row illustrates the format. Use **Pass**, **Fail**, **Not run**, or **Not applicable**, with a reason for the last two. Keep implementation evidence separate from tests actually run, record untested behavior as untested, and list out-of-scope findings separately without implementing them.

Check IDs are stable references. Add new IDs rather than renumbering or reusing existing ones; a changed check needs an explicit version note.

## Acceptance checks

### 1. Share capabilities across interfaces

- **Check 1.1 — Shared behavior.** Through each supported interface, discover, invoke, inspect, and recover from the same operation. Verify consistent meaning, permissions, and feedback.
- **Check 1.2 — Shared validation.** Try invalid input and a failed save through each supported interface. Confirm unchanged stored state and actionable errors.
- **Check 1.3 — Adapter boundaries.** Trace a capability through its adapters. Adding an interface must not require a second implementation of domain behavior.
- **Check 1.4 — Purpose in the tool's description.** Inspect the tool definitions actually delivered to each supported agent interface. Verify that they convey the user need, result, and limits, distinguish related operations, and preserve the shared capability's meaning.
- **Check 1.5 — Interfaces fit their callers.** Trace one user job through UI controls, agent actions, and CLI commands where supported. Include a read, an editor-opening request, and a supplied-content update: only the last may change stored content. Different action shapes must preserve scope, validation, and recovery.
- **Check 1.6 — Screen actions fit the caller.** Inspect the tool listing served to each interface. By default, screen actions must be absent from callers that do not share the user's screen, and rejected if invoked by name, while remaining available to the embedded agent. Where an external chat app is offered screen actions, verify that they work through that interface and that the agent uses them only when the user explicitly asks. Test both cases.
- **Check 1.13 — Screen actions run through the application's own state.** For each screen action offered to the embedded agent, verify that it changes the screen through the same event or method a person's click uses, so the screen and its recorded state agree afterwards, and that it synthesizes no input events. Verify that the directions the agent gives for a screen action come from code, and that a screen action refuses, and says why, while the user has unsaved work in the place it would change.
- **Checks 1.7–1.11** cover the inspectable registry; see [Make the capability registry inspectable](#make-the-capability-registry-inspectable).
- **Check 1.12 — Tools for repeated jobs.** From test results and use, list the jobs users ask for again and again that the agent does by combining general tools. Where one does not perform as well as you need, consider a tool made for that job, as general as the job allows (merge any two or more items, not one pair). If one is added, keep the general tools, and rerun the whole suite (Check 4.5).
- **Check 1.14 — Views supplement a complete text answer.** MCP Apps lets a chat app display an interactive view supplied by an application's MCP server. The tool must also provide a complete text answer for chat apps that cannot display the view.

  Test the tool through two client connections: one that announces support for views and one that does not. Verify that:

  - Only the client that announces support receives the view.
  - Both receive a text answer containing every figure shown in the view.
  - The text and view use the same code-produced data.
  - The text gives each figure's meaning, units, and date, and says when data is unavailable or out of date, as the view does.
  - When a view is supplied, the accompanying text tells the model to add useful interpretation rather than repeat what the view shows.

  Verify the resulting conversation in both clients; an instruction to avoid repetition does not prove that the model follows it. Also make the view fail to display in a client that announced support, and confirm the conversation still makes sense from the text answer alone.

### 2. Help users finish the job

- **Check 2.1 — Subject and task.** Discuss a problem, then ask "open it so I can fix that." Verify the target, the destination, and the absence of unrequested changes.
- **Check 2.2 — Context corrections.** Change selection and ask about "this one"; correct a prior request; try an ambiguous reference. Follow clear intent and clarify material ambiguity.
- **Check 2.3 — Complete scope.** Request every member of a named list. Verify all intended records are handled on the first request and unrelated records are preserved.
- **Check 2.4 — Visible outcomes.** Exercise a multi-step job and undo. Check saved state and every visible representation, then repeat with the result offscreen and unsaved edits present. Explain unfinished work without obscuring the result or stealing focus.
- **Check 2.5 — Jobs in ordinary language.** Express a real job several ways without naming controls or tools, including an exploratory question, an information request, a clear change request, and an ambiguous acceptance of two offers. Grade useful outcomes, appropriate reads or actions, and necessary clarification; do not require one prescribed tool sequence for every phrasing.
- **Check 2.6 — Additive references.** Request one action, then "the other event type too." Verify the inherited subject, new kind, complete intended scope, and preservation of earlier settings. Repeat after an unrelated turn and with several plausible subjects; clarify only when needed.
- **Check 2.7 — Repair after a wrong turn.** Include an actual mistaken assistant response before a user correction. Verify the correction updates the original request rather than the mistaken substitute. Score resulting state or calculation, answer truthfulness, and task completion separately; record a lost reference or metric substitution as a failure reason. Do not grade exact wording.
- **Check 2.8 — Reference evidence and boundaries.** Resolve a returned object, then exercise an expired or missing reference, a stale or deleted object, changed selection, a cross-workspace identifier, a failed write, and ambiguous antecedents. Verify scope and current permissions, refresh values when required, and never treat a proposed or rejected action as committed. Export only policy-permitted reference evidence.
- **Check 2.9 — Revise a named result without changing the original.** Revise a computed result by its explicit ID and changed inputs. Verify unchanged inputs and original dated source data are preserved, the original result is untouched, a new result ID is returned, and all constraints are revalidated. Test invalid changes and missing, expired, or inaccessible IDs; never fall back to the latest result. Confirm that describing, referencing, or revising a hypothetical plan does not execute it or save it as a user setting.
- **Check 2.10 — Familiar forms, documents, and spreadsheets.** For a job whose data lives in a familiar form, document, spreadsheet, or calendar, have the agent make a change. Verify the change lands in the form, document, or spreadsheet itself, appears the way it already shows changes, and passes its own validation. For a review task, verify the item under review stays primary on screen, the decision is made only through the screen's controls, and the agent points to evidence rather than recommending a verdict unless asked.

### 3. Enforce the safety line in code

- **Check 3.1 — Atomic outcomes.** Fail a single operation's save and retry a completed request. Verify accurate outcomes, no partial saved mutation, and no duplicated write.
- **Check 3.2 — Recovery.** Undo and redo a change. Verify the affected state and visible views; introduce an intervening edit and confirm recovery does not silently overwrite it.
- **Check 3.3 — Enforced authority.** Call a forbidden operation directly and through every supported interface. Verify execution rejects it independently of prompts and tool listings.
- **Check 3.4 — Approval applies to this exact change.** For actions requiring approval, try none, approval claimed in agent text, and changed proposal details, including consequential reversible actions and an interface without an approval channel. None may bypass the gate.
- **Check 3.5 — Combined impact.** For an operation that needs approval at scale, verify that the agent has an operation that takes one item or many, whose approval rule sees the whole change, and report any path where repeated single-item calls reach the same result without approval.
- **Check 3.6 — Data and resource boundaries.** Place hostile instructions and prohibited data in inputs and stored records. Verify model-input restrictions and execution policy; exhaust call, time, cost, and retry limits and inspect the reported partial outcome.
- **Check 3.7 — Guards.** For each operation with a guard, list its question, the data it passes to the decision model, the confidence at which a yes refuses the change, and what the refusal tells the agent. Measure its decisions on labelled conversations not used while writing it: how often it refuses a request that should go ahead, and how often it allows one it should refuse. Run the suite with and without it. Confirm the change is refused when no decision comes back, and that the decision model is given application data only where a measurement showed it helps.
- **Check 3.8 — Audit record.** Run turns that apply, refuse, and fail a change, and one where a review rewrites the reply. Verify one record per attempted change with its outcome and the checks that decided it, one record per reply with the text the user saw where the capture policy includes it and a mark that it was left out where it does not, and undo and redo recorded as new records that leave earlier records unchanged. Verify an evaluation compares each turn's records with what actually happened. Where the records go and how long they are kept is set in logging configuration, not in code.
- **Check 3.9 — Undo scope.** Have the embedded agent change a field, then use the general Undo command; verify it reverts that change and names it. Have an external client change a field; verify the general Undo leaves it alone, that it does not clear the user's Redo, and that it can still be reversed from the change history.
- **Check 3.10 — Uncertain outcomes.** Let a change be saved and drop its reply before the caller receives it. Retry the request and verify that the change is applied once, that the retry returns the first outcome, that each attempt is recorded with its own identifier and both with the change's identifier, and that until the outcome is known the user is told the change is pending, not that it failed.
- **Check 3.11 — Stopping a request.** Stop a request of several changes after the first is saved and before the second starts. Verify that the second does not run, that nothing is left half-saved, that the first stays saved and can be undone, and that the user is told which changes were saved and which were not.

### 4. Give the model clear tools and current evidence

- **Check 4.1 — Relevant reads.** Verify that data questions make relevant reads, navigation follow-ups avoid unrelated reads, and general explanations need no application data. Expose failed reads without inventing facts.
- **Check 4.2 — Current evidence.** Change a quantity between turns; verify the next factual answer reads it. Change a summary's source data and verify source dates and staleness are communicated.
- **Check 4.3 — Delivered history.** Rewrite an answer through review, fail an action, then continue the conversation. Verify history reflects the delivered answer, the actual outcome, and the current selection.
- **Check 4.4 — Application-written text.** List the answer text the application can produce itself: save confirmations, directions to a setting, calculated results, the old and new place of a moved item, pending approvals. Verify the application shows each one as its own text and the model supplies only the choice (the destination, the operation, whether to ask). Confirm no prompt or tool description asks the model to repeat such text.
- **Check 4.5 — Whole-suite rerun.** After adding a capability, changing a tool description or result text, reordering tools, or adding a prompt sentence, run every case, not only the ones the change was meant to fix. Compare per-case results with the previous run and investigate any case that dropped, including cases unrelated to the change. Fix the tool description or result a drop exposes rather than the tool order. When the suite is too slow or costly to run in full after every change, run the cases closest to the change each time and the full suite before each release, and say in the report which was run.
- **Check 4.6 — One current copy.** Where data goes with every message, hold a conversation of ten or more turns that changes that data, and read what the model received on the last turn. Confirm it holds one copy of the data, the current one.

### 5. Explore with persona-driven users

- **Check 5.1 — Credible scenarios.** Inspect persona starting data, goals, and private backstory. Check plausibility with human observations; do not treat simulations as evidence of customer demand.
- **Check 5.2 — Adaptive exploration.** Run varied personas and adversarial inputs. Verify conversations can adapt within enforced budgets and capture transcripts, calls, errors, and state changes.
- **Check 5.3 — Preserved failures.** Reproduce a real-user or persona failure from saved starting state. Keep a fixed regression scenario alongside continued exploratory runs.
- **Check 5.4 — Actions available to simulated users.** List the actions the persona harness lets the simulated user take. Each must be one the person could take on the screen (typing, clicking a visible control such as Approve or Deny). Try an action the person could not take, such as approving a request with no approval control shown, and confirm the harness neither performs it nor records it as done.

### 6. Evaluate the user's outcome

- **Check 6.1 — Outcome evidence.** Check a conversation that sounds successful but misses part of the task. Verify evaluation catches the saved-state gap and records corrective user effort.
- **Check 6.2 — Judge calibration.** Compare model judgments with labels of the same evidence. State who made the labels: a person, or an agent whose labels a person sampled and decided. Investigate disagreements and report review failures as unavailable rather than as passes or failures. For each judge that is asked more than once, show from the labeled set that taking the majority of several answers improves agreement; a judge whose errors repeat is asked once.
- **Check 6.3 — Comparable runs.** Compare versions using fixed starting data and criteria. Record model, prompt, tools, costs, latency, and individual failures; report exploratory runs separately.
- **Check 6.4 — Tool independence.** Stop the observability platform and run a suite. The same report and exit code must result, and the report must say what was and was not recorded. Where cases are pushed to the platform, edit one case in the platform's interface and confirm the next run refuses with a conflict rather than measuring the edited case.
- **Check 6.5 — Served model.** Read back a run and confirm every generation records the model that served it. Request an alias and confirm a dated snapshot, where the provider uses one, appears in the record; request a dated snapshot and confirm a different served model is flagged. Where the provider does not report which version served the call, confirm the record says so instead of repeating the requested name.
- **Check 6.6 — Checks protect outcomes.** For each check in a suite, name what it protects: trust, a policy line, or completion of the job. Run a correct answer phrased differently from the expectation and confirm no check fails it on wording alone. Confirm a check that fails good answers is retired and replaced, not edited in place.
- **Check 6.7 — Grade only model-written text.** For each check that reads answer text, mark whether that text is written by the model or by code. A check that grades the model's restatement of code's text is a design finding: move the text to the application (Check 4.4) and grade the choice or the state in code. Confirm judges read only model-written text, and that application-written text is marked so they can tell the difference.
- **Check 6.8 — Grader assignment.** For each check in a suite, name its grader: code, a narrow judge, the broad judge, or a person. Flag any judge deciding something code can compute (state, arithmetic, identifiers, the destination chosen) and any agent-written figure the application could have computed. Confirm persona agents and independent reviewers produce material and second opinions, not pass or fail.
- **Check 6.9 — Unseen cases for the same kind of task.** For each case found in use or by a persona, find a held-out case for the same job with different items and words, written by someone other than the person making the fix, or by a separate session whose cases the fixing session cannot read. Confirm the tooling refuses to run it during fixing unless asked explicitly. Develop the fix against the visible cases, freeze it, and only then run the held-out cases. Confirm that no fix, description, or example copies a held-out case's items or phrasing; vocabulary of the job that any user would use is expected to be shared. A held-out case may already pass before the fix; record that as a result. Once a held-out case has been run, read its result, move it into the visible cases, and replace it with a fresh one. The same applies when an automated optimizer, rather than a person, searches over prompts or tool descriptions.
- **Check 6.10 — Reliability across attempts.** For jobs where consistency matters, report pass^k beside the pass rate, with k and the number of attempts stated. Confirm the report does not present a pass rate alone as how often a repeated job succeeds.
- **Check 6.11 — Injected failures.** Run the suite with read failures, write failures, and timeouts injected. Confirm truthful reporting and complete recovery, and compare pass rates and pass^k with the clean run.
- **Check 6.12 — Wording borrowed from test cases.** Review tool names, descriptions, fixed lists of choices, and messages for wording that matches a test case or a reported conversation. Try each with a request nobody has used before. Remove wording that serves only one case, and rerun the suite.
- **Check 6.13 — One place to see what happened.** From a failed result, open the conversation as a developer and as a coding agent. Both must reach the same record: what the model was sent, the tools it called and what they returned, the state after each turn, and each check's verdict.
- **Check 6.14 — Release decision.** Before a release run, confirm a written rule names who decides, the failures that block the release, the failure rate accepted for the rest, and what makes a run inconclusive, such as ungraded judgments or a required check that did not run. Confirm the report applies the rule as written and gives cost and time for each completed job as well as for each model call.
- **Check 6.15 — Experiment records.** Pick an improvement a report claims and follow its link to the experiment record. Confirm the record gives the change, the model and application versions, the cases and the number of attempts, the grading criteria, the result, and what the experiment could not show.

### 7. Put the principles to work

- **Check 7.1 — Scoped integration.** Trace one assigned job before and after integration. Verify preserved behavior, shared execution, feedback, and recovery through existing and agent interfaces.
- **Check 7.2 — Bounded delivery.** Report in-scope gaps against check IDs. Keep unrelated improvements separate; do not add interfaces, redesign the application, or change policy without task authorization.

## Evaluation infrastructure

These practices make section 6 of the principles, and its companion paper [Evaluating Agents in Applications](beyond-chat-evaluating-agents.md), operational.

**Keep the case definitions in the repository and let the observability platform hold the results.** Keep each case, its grader, and its starting data in the repository, push what the observability platform needs, and push one way only: a case edited in the platform's interface blocks the next run with a conflict instead of silently changing what was measured. If the platform is stopped, every evaluation still runs and writes the same report; only the shared view is lost (Check 6.4). Keep the number of modules that import the platform's SDK small, so retargeting to another platform touches the recorder, the dataset transfer, and the links a results page writes, and nothing else.

**Define the suite yourself, because the platforms we used had no concept of one.** They know datasets, runs, sessions, and traces. A team thinks in suites: the cases, the grader and its exact version, the starting data, the spending cap, what triggers a run, and where the report goes. Write that definition once and derive every name the platform sees from it. Own the vocabulary too: an *experiment* compares two or more arms that differ in one thing; the thirtieth execution of a suite on unchanged code is a *run*.

**Retire a case instead of editing it.** A dataset file carries its active cases and a retired list mapping each retired case to its reason. Pushing archives the hosted copy under its own identity; a corrected case joins under a new one. A case listed as both active and retired is an error at load.

**Record what actually served the call.** A model name is often an alias the provider can move to a new snapshot without notice. Capture the model requested, the version the provider reports serving (or that it reported none) on every generation, and the application's commit on every run (Check 6.5). Choose deliberately between a pinned version and an alias the provider moves: an alias picks up the provider's changes without a release of the application, and a pinned version keeps the selected model version fixed until you change it. Where stable behavior matters, evaluate a new version before moving production to it.

**Ask for a structured verdict.** When a model's entire output is a decision, request a reply in a format the API enforces rather than JSON embedded in prose, and give a simulated user a field to say it is finished rather than a keyword the code searches for. A reply that cannot be read is *unavailable*, never zero and never a failure.

**Build narrow checks as data.** A fabrication check is a question, a feedback template, and the cases it must and must not trip. Measure each question's yes-rate on planted failures and on real clean answers before wiring it into the delivery path. Ask each question once unless calibration shows its errors vary between askings; only then vote, asking until a majority is settled (two agreeing answers settle a three-vote check). A judge whose errors repeat gives the same wrong answer every time it is asked. Let code merge the verdicts. Record each check's vote and quoted evidence in the trace, under the review it belongs to.

**Keep every review's reasons in the record.** A review that a later review supersedes must keep its verdict, its flags or failed checks, and its feedback, and every review and rewrite must be recorded, with its text and feedback where the capture policy permits and a mark that the content was left out where it does not. Many observability backends serve verdicts through their APIs but not span contents, so the run report has to carry the reasons itself.

**Give people a results page.** Generate a results page from the run reports, never by hand. Name each evaluation by the question it answers, count results by conversation with the failed checks in plain words beneath, link each conversation to its trace, show a short history per evaluation, and put an outline of what happened (the request, the reads, the writes and any refusal, each review's verdict and reason, the answer) under each failed conversation. A link from a failure must open a page that shows the failure.

**Read the prompt the model received.** Traces show the request exactly as it left the application. Read them: they reveal formatting mistakes in instructions, rubrics that quote their own test cases and so can never fail them, and calls to interfaces the vendor has deprecated.

## Make the capability registry inspectable

When implementing a registry, provide three connected contracts: what the application can do, what a particular caller was offered, and what actually executed. A reusable inspection tool should be able to join these records without interpreting tool names or scraping the interface. This is a proposed application contract, not an MCP or observability standard; adopt it explicitly and report which parts are supported.

**Build on established observability.** Use existing instrumentation, collectors, storage, and access controls. OpenTelemetry supplies a collection and export foundation with guidance on sensitive data; platforms such as Langfuse provide trace access controls, masking, and retention. [15](https://opentelemetry.io/docs/security/handling-sensitive-data/) [16](https://langfuse.com/docs/administration/rbac) For model and agent spans, use the OpenTelemetry GenAI semantic conventions, which cover agent operations (`create_agent`, `invoke_agent`), MCP spans, and a `gen_ai.evaluation.result` event for evaluator results. [23](https://github.com/open-telemetry/semantic-conventions-genai) They are marked Development and the repository had no release as of October 3, 2026, so expect names to change and record the convention version used. Installing an SDK does not establish secure access. This contract adds application meaning those systems cannot infer: stable capability identity, offered-tool snapshots, trusted authorization outcomes, and committed state changes. It requires no new tracing protocol, authentication system, collector, or viewer.

| Responsibility | Owner |
| --- | --- |
| Trace transport, storage, viewer authentication, access controls, retention and deletion | Established observability infrastructure, configured for the deployment |
| Which data may be captured or exported; action identity, caller context, validation and actual effects | Application capability and shared execution layers |
| Pause, overrides, replay, undo and other debugging actions | Explicit application capabilities with separate execution authorization |

Represent the fields below using existing spans, events, attributes, and protected payload references where practical. Reuse supported semantic conventions and identify their version; keep additional fields in a documented application namespace. The field names define the logical contract; they do not require duplicating native records.

**Keep inspection private and scoped.** Enabling instrumentation must not expose a public endpoint, enable payload capture, or grant a debugging agent trace access. Start with necessary execution metadata; capture content only under explicit policy. Keep app, user, and workspace boundaries intact when aggregating. Collector ingestion credentials must not grant trace-reading or execution privileges. Filter prohibited data before it leaves the application; backend masking is additional protection. Record authorization outcomes as decisions or protected references, never credential or approval-token contents. Retrieved traces are untrusted material for a debugging agent.

**Register actions with their owner.** Each capability declares its actions alongside their implementation. Registration binds an action descriptor to its handler, input and output validation, and policy. Reject duplicate action IDs and unresolved handlers at startup. A registry can be a collection of ordinary modules and functions; it need not be a separate service or expose MCP.

An action is the stable unit of invocation. A capability groups related actions: `record.notes.read`, `record.notes.open_editor`, and `record.notes.replace` belong to `record.notes`. Opening an editor changes the screen; replacing notes changes stored data. Declare their inputs, results, and effects separately, even if one interface groups them under a single control.

**Export a versioned catalog** through an in-process function or serialized export; no network discovery endpoint is required. Use these field names at the export boundary:

| Record | Required fields and meaning |
| --- | --- |
| Catalog | `contract_version`, `app_id`, `app_version`, `catalog_revision`, `actions`. App and action IDs are stable; the revision identifies the exact catalog contents. |
| Action | `action_id`, `capability_id`, `action_version`, `title`, `description`, `input_schema`, `output_schema`, `effects`, `surfaces`, `policy_ref`, `recovery`. Schemas declare their JSON Schema dialect. The description states purpose, limits, and distinctions from neighboring actions. |
| Effects | A nonempty array drawn from `read` (reads data), `screen` (changes what the application's screen shows), `write` (changes stored data, in this application or another system), and `external` (reaches a system outside the application, whether to read or to write). Declare all that apply; an action that changes data in another system declares both `write` and `external`. Do not infer behavior from verbs such as get or update. |
| Surfaces | Supported callers: `ui`, `embedded_agent`, `cli`, or `mcp`. These describe possible exposure, not current authorization. |
| Recovery | `mode`: `none`, `undo`, or `compensate`, plus an explanation of limits. Declaring recovery does not establish that a particular call can still be recovered. |

Use contract version `1` for this shape. A breaking export change increments `contract_version`; an incompatible action change increments `action_version`; any descriptor change, including wording, changes `catalog_revision`. Never reuse an action ID for a different purpose. Document extensions under `extensions`; consumers tolerate unknown extension fields.

**Export MCP tool annotations from the catalog.** When an action is served over MCP, derive its annotations from the descriptor so an MCP host shows accurate risk labels: `readOnlyHint` says whether the action modifies its environment, so it is true when `effects` contains no `write` and no `screen`; `openWorldHint` says whether the action reaches outside systems, so it is true when `effects` contains `external`. The two are set independently: a web search is read-only and reaches an outside system. The catalog does not yet say whether a write only adds or may destroy, or whether repeating a call has no further effect, so declare those under `extensions` and map them to `destructiveHint` and `idempotentHint`. `recovery` does not set `destructiveHint`: an undoable deletion is still destructive. Without these declarations, leave the MCP defaults (`destructiveHint` true, `idempotentHint` false). Annotations are hints a client must treat as untrusted unless the server is trusted; they never replace the policy check at execution (Check 3.3). [20](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)

**Record the tools each caller was actually offered.** A full catalog does not prove that a model saw a tool. For each model request, record `model_request_id`, `catalog_revision`, and a `tool_surface` snapshot of the exact provider-facing names, descriptions, and schemas delivered, subject to the capture policy. Map each exposed tool to its `action_id` and `action_version`. Keep unsupported, policy-denied, and temporarily unavailable actions distinguishable; recheck policy at execution, since a listing is neither authorization nor a reservation. Caller identity and approval evidence come from the adapter's trusted context, never from model-supplied arguments.

### Route execution and observation through the same boundary

All supported callers invoke the registered action through shared execution. Adapters translate arguments and results; they do not call a second implementation or bypass validation. Internal composition may call another capability through this boundary as a child invocation.

**Shared state describes the screen; it does not write stored data.** In frameworks such as AG-UI, the frontend and the agent both read and modify a shared state object. [24](https://docs.ag-ui.com/concepts/state) Any change to stored data that arrives through that state must be executed as a registered action through shared execution, or it bypasses policy, validation, and undo.

```text
UI / embedded agent / CLI / MCP adapter
  → resolve action and establish trusted caller context
  → record invocation; check policy and validate input
  → execute the owning handler; validate result and record actual effects
  → complete the persistence/history guarantees required by that action
  → return the application outcome and emit its observation
```

**Publish structured observations** at this boundary, for successes as well as errors, distinguishing these identities:

| Field | Meaning |
| --- | --- |
| `interaction_id` | One user interaction, potentially several model requests and actions. |
| `model_request_id` / `tool_call_id` | Provider identifiers where applicable; null for direct UI actions. |
| `invocation_id` / `parent_invocation_id` | Unique execution attempt and its enclosing invocation. Retries get new IDs linked through `retry_of`. |
| `action_id`, `action_version`, `catalog_revision` | The exact application contract used. |
| `surface` / `actor_kind` | Entry surface and initiator (`human`, `agent`, or `system`), assigned by application code. |
| `trace_id` / `span_id` | Optional correlation with existing tracing; not substitutes for application identities. |

Represent start and finish with a native span lifecycle or explicit `started` and `finished` records carrying an `event_id`, `invocation_id`, timestamp, and sequence number. Completion includes duration, permitted input and result or references, and status: `succeeded`, `rejected`, `failed`, `cancelled`, or `pending`, with an application error code distinguishing invalid input, policy denial, conflicts, and execution errors. Keep execution status separate from effects: report `effect_status` as `none`, `committed`, `partial`, or `unknown`, with change and revision references. An interrupted process may leave a start with no finish; a viewer must show an incomplete observation, not invent an outcome.

**Expose context deliberately.** When capture is authorized, record or reference the messages actually sent, model and configuration, application context supplied, response, and usage. Otherwise record permitted metadata and mark content omitted. Keep records unaltered for their retention period; deletion that policy authorizes is a separate, recorded step. Each payload declares `capture_state` (`complete`, `redacted`, `omitted`, or `truncated`). Record sampling and dropped events where known; absence of a trace is not proof nothing executed. Observation-export failure must never turn a committed action into a reported failure or trigger its retry. For MCP, distinguish the local client call from execution inside the remote server, and mark remote effects as unobserved when only one side is instrumented.

### Declare inspection support and test the contract

Export a support manifest naming which of `catalog`, `tool_surface`, `model_requests`, `invocations`, `state_changes`, and `presentation_context` are implemented, with uncovered paths and capture restrictions, so a viewer can show partial coverage honestly. Observation grants no execution authority: pause, argument replacement, overrides, replay, and undo are separately authorized capabilities, and replaying a trace must never rerun writes against live state by default.

- **Check 1.7 — Inspectable catalog.** Export a catalog and validate required fields, unique IDs, versions, schemas, and handler bindings. Verify that UI and agent mappings resolve to the same registered owner. Change a description and confirm the catalog revision changes.
- **Check 1.8 — Offered versus executed.** Capture a real model request and verify its recorded list of offered tools matches the definitions actually delivered. Follow a resulting tool call to its resolved application action. Verify direct UI actions are observable without fabricated model-call IDs.
- **Check 1.9 — Records match what happened.** Exercise success, validation rejection, policy denial, handler failure, cancellation, and partial or uncertain effects where supported. Compare observations with actual state. Interrupt execution and verify an incomplete trace is not labeled successful; fail the exporter and verify a committed write is not retried.
- **Check 1.10 — Portable inspection.** Read the catalog, support manifest, and observations through an independent consumer without importing application handlers. Follow local and MCP calls where supported, recognize coverage gaps, and verify redaction occurs before export. Inspection access must not grant permission to invoke or replay actions.
- **Check 1.11 — Protected observation.** Verify that instrumentation alone exposes no public inspection endpoint and captures no unauthorized content. Test catalog and trace access across app, user, and workspace boundaries, collector credential scope, redaction before export, and configured retention and deletion. Confirm that malicious instructions in a recorded result, and an observer's request to grant itself access, cannot authorize debugging actions. Verify that every recorded conversation says so to the person in it, including a tester typing into a simulated user's conversation, and that production conversations reach the trace store only under a separate, explicit decision.

Start with one capability and prove the full path before extending coverage.

## Make references part of the capability contract

Let the model interpret what the user asks for, and have the application store inputs and results and recompute them. Use the existing agent runtime to preserve conversation and tool history; do not introduce a separate conversation interpreter, slot tracker, or program language merely to handle follow-ups. Keep one authoritative capability definition in code (schemas, domain kinds, concise descriptions including everyday names, validation and operation semantics) and derive each interface from it.

| Owner | Responsibility |
| --- | --- |
| Model | Resolve the user's task, references, additions, and corrections from the original requests and available history; ask when material ambiguity remains. An interpretation is revisable, not evidence of user intent. |
| Existing agent runtime | Preserve relevant turns and tool evidence with source links. Keep the original request distinct from a mistaken interpretation. Never invent history or assume the latest result is the intended subject. |
| Capability definition and results | Declare subject types, units, kinds, supported choices, and add, remove, or replace semantics. Give results IDs, explicit subjects, effective inputs, and actual outcomes. For invalid input, identify the rejected value and the available choices where safe. |
| Application calculation and storage | Store immutable inputs and results with owner scope and expiry. Resolve explicit references under current access rules, merge validated changes, revalidate the complete inputs, recompute, and return a new result. |

**Return outcomes that can be referenced.** A tracking result shows the affected subject, the kind, the operation, the saved status, and the resulting selection. Prefer add as the default for membership changes and require a deliberate replace, whose result names the removals. An ID or a receipt does not establish success without execution evidence.

**Revise computations from stored inputs.** Calculation capabilities may accept `based_on: <result_id>` plus a `changes` object; there is no implicit "most recent result." Preserve the original, return a new ID with the effective inputs, and present the revision in the user's terms: "I'm changing the maximum term from 12 to 18 months." Referencing or revising a hypothetical plan never executes it or saves it as a setting. Retain original dated source data by default; refresh is a separate, explicit request producing new provenance.

**Keep scope and evidence explicit.** Stored inputs and results have an owner, scope, and expiry; IDs grant no authority. Treat names and result text as untrusted data. Preserve multi-turn cases for additions, corrections, removals, several subjects, revisions, references after unrelated topics, and material ambiguity, and check state, truthfulness, and completion separately.

## Assess test harnesses and deployment risks

Persona runners, evaluators, debuggers, and collectors are part of the system's threat model. A runner that simulates a user may still hold real provider credentials, invoke write capabilities, send context to external services, and save sensitive artifacts; a test-data directory is not a sandbox. For each mode (headless, interactive, live-service), document the identities and credentials used, permitted data and destinations, control endpoints, capture policy, persistence and cleanup, and resource limits. Separate synthetic tests from explicitly authorized live tests.

**Report the evidence and its limits, and make no assurances.** These principles are engineering guidance, not a certification, a complete threat model, or a guarantee of security, privacy, regulatory compliance, or fitness for a purpose. A passing test establishes only the behavior observed under its recorded conditions. Avoid claims such as "secure" or "fully isolated" based on adopting this architecture. Each organization must assess its own deployment, data, integrations, and obligations, and this guide does not replace qualified security, privacy, or legal review.

## Keep persistent context small

Read the principles and this guide in full for an initial review. For routine sessions, keep the ownership split, check index, and working rules from [the compact checklist](beyond-chat-agent-checklist.md) in the project's persistent instructions, and load detailed checks when a scoped task needs them. The checklist only summarizes this guide; it is not a separate contract.

**Scope.** Multi-user isolation, concurrent edits, network operation, and detailed cost forecasting need their own designs and tests; shared contracts help organize that work but do not solve it.

Sources [15], [16], [20], [23] and [24] are listed in the principles' [Foundations and Further Reading](beyond-chat-building-agents-into-applications.md#foundations-and-further-reading).
