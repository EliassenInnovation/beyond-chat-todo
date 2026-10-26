# Implementation and acceptance checks

For coding agents and the engineers who direct them

<a class="md-button" href="../agent-guide.md" download>Download for coding agents (.md)</a>

Use the [checklist builder](../guide/checklist-builder.md) to select and adapt checks for
your application, preview the handoff, and download it for a coding agent.

The download includes the complete guide and acceptance checks, generated from the same
source on every build.

> Security scope: These practices address agent behavior and do not make an application secure. Authentication, authorization, encryption, transport security, and other application security controls require separate design and review under your organization's security policies.

This chapter is part of the [guide](../index.md), which defines the
approach. These checks help engineers and coding agents apply its principles to a particular
application. Select and adapt them to the architecture, priorities, and behavior you agree
to build. Record which checks apply, how you adapted them, and the reasons for setting others
aside. A gap against an optional example is a design choice to discuss, rather than an
automatic implementation failure.

The chapters explain the principles and tradeoffs; the checks below help verify your chosen
implementation. For an initial architectural assessment, start with
[using the guide with a coding agent](../guide/apply.md#use-this-guide-with-a-coding-agent).

## Quick checklist

<a id="keep-persistent-context-small"></a>

Keep the project's persistent instructions short: name the adopted principles, link to
this page, and record the team's decisions about which checks apply. Load the relevant
chapters and detailed checks when a task needs them. This keeps the guide as the main
reference while preserving decisions specific to the application.

Assign a capability, the interfaces to examine, the changes allowed, and the check IDs.
For example: "Review rescheduling through the screen and command line against Checks
3.1–3.7. Report findings; leave the code unchanged." For an implementation task, name the
changes the team has agreed to make.

Use the ownership summary and working rules below during that task, then report evidence
against the applicable acceptance checks.

### Who owns what

- The capability owns what an operation is: its purpose, actions, inputs, checks on those inputs, what it changes, its limits, the names and meanings of its inputs, and results that later requests can refer to.
- The model interprets what the user is referring to and what a correction changes.
- The code that runs the agent keeps the user's requests and tool history. Application code stores inputs and results and recalculates. Start with conversation and tool history; add explicit task state when the workflow or evaluation evidence calls for it.
- Shared execution, the code every operation runs through, owns policy, approval, saving, history, undo, and reporting what actually happened.
- Each interface owns how a caller finds and reaches an operation, and how the result is shown. Screen controls, agent tools, and command-line commands are each designed for their caller and share the same behavior underneath; one capability need not be one tool.

A user's job may need several capabilities. The agent combines them; application code owns any steps that must happen in order, or all together, and how to recover when one fails.

### Inspection and records

When the task covers making the application inspectable, give each action an ID that does not change, a versioned description of its inputs, and a statement of what it changes; send every caller through shared execution. Record the tools each caller was actually offered, and link each call, from inside the app or through MCP, to what happened in the application. Use existing tracing tools, with a written mapping of the application's details onto them. Record conversation content only where policy says so; limit who can read the records, and remove protected data before it leaves. Permission to read the records does not include permission to change execution or rerun actions. See [Checks 1.7–1.11](#make-the-capability-registry-inspectable) and the
[inspection appendix](../reference/inspection.md) for an example record format.

References to earlier work: preserve the person's words, actual tool calls and results,
and relevant application state so the agent can resolve follow-ups. Where a workflow needs
it, application-owned action groups or saved calculation inputs make recovery and revisions
more reliable. The [request chapter](../guide/requests.md#interpret-follow-up-requests)
explains the principle; the [appendix](../reference/conversation-references.md) illustrates
optional record formats. Adapt Checks 2.8–2.9 when adopting those features.

### Check index

- [1.1](#check-1-1) Shared behavior; [1.2](#check-1-2) Shared validation; [1.3](#check-1-3) Adapter boundaries; [1.4](#check-1-4) Purpose in the tool's description; [1.5](#check-1-5) Interfaces fit their callers; [1.6](#check-1-6) Screen actions fit the caller; [1.7](#check-1-7) Inspectable catalog; [1.8](#check-1-8) Offered versus executed; [1.9](#check-1-9) Records match what happened; [1.10](#check-1-10) Portable inspection; [1.11](#check-1-11) Protected observation; [1.12](#check-1-12) Tools for repeated jobs; [1.13](#check-1-13) Screen actions run through the application's own state; [1.14](#check-1-14) Views supplement a complete text answer.
- [2.1](#check-2-1) Subject and task; [2.2](#check-2-2) Context corrections; [2.3](#check-2-3) Complete scope; [2.4](#check-2-4) Visible outcomes; [2.5](#check-2-5) Jobs in ordinary language; [2.6](#check-2-6) Additive references; [2.7](#check-2-7) Correction after a misunderstanding; [2.8](#check-2-8) Reference evidence and boundaries; [2.9](#check-2-9) Revise a named result without changing the original; [2.10](#check-2-10) Familiar forms, documents, and spreadsheets; [2.11](#check-2-11) Accurate personal context; [2.12](#check-2-12) Current personal context; [2.13](#check-2-13) Relevant questions and remembered answers.
- [3.1](#check-3-1) Atomic outcomes; [3.2](#check-3-2) Recovery; [3.3](#check-3-3) Enforced authority; [3.4](#check-3-4) Approval applies to this exact change; [3.5](#check-3-5) Combined impact; [3.6](#check-3-6) Data and resource boundaries; [3.7](#check-3-7) Guards; [3.8](#check-3-8) Audit record; [3.9](#check-3-9) Undo scope; [3.10](#check-3-10) Uncertain outcomes; [3.11](#check-3-11) Stopping a request.
- [4.1](#check-4-1) Relevant reads; [4.2](#check-4-2) Current evidence; [4.3](#check-4-3) Delivered history; [4.4](#check-4-4) Application-written text; [4.5](#check-4-5) Whole-suite rerun; [4.6](#check-4-6) One current copy.
- [5.1](#check-5-1) Credible scenarios; [5.2](#check-5-2) Adaptive exploration; [5.3](#check-5-3) Preserved failures; [5.4](#check-5-4) Actions available to simulated users.
- [6.1](#check-6-1) Outcome evidence; [6.2](#check-6-2) Judge calibration; [6.3](#check-6-3) Comparable runs; [6.4](#check-6-4) Tool independence; [6.5](#check-6-5) Served model; [6.6](#check-6-6) Checks protect outcomes; [6.7](#check-6-7) Grade only model-written text; [6.8](#check-6-8) Grader assignment; [6.9](#check-6-9) Unseen cases for the same kind of task; [6.10](#check-6-10) Reliability across attempts; [6.11](#check-6-11) Injected failures; [6.12](#check-6-12) Wording borrowed from test cases; [6.13](#check-6-13) One place to see what happened; [6.14](#check-6-14) Release decision; [6.15](#check-6-15) Experiment records.
- [7.1](#check-7-1) Scoped integration; [7.2](#check-7-2) Bounded delivery.

IDs identify the checks below. Keep them stable when reorganizing the page; assign new IDs
to new checks and document changes in meaning in the revision note.

### Seven working rules

1. Look before proposing. Follow a real request through execution, saving, feedback, and recovery.
2. Make gaps concrete. Separate what is built, what is tested, and what is missing; cite the evidence.
3. Fix the shared owner. Keep the application's behavior and its rules out of individual interfaces and prompts. Before adding prompt rules or another model to supervise, read what the model was actually sent: the tool descriptions, the tool results, and any data sent with each message. Use the rerun procedure in [Check 4.5](#check-4-5) after changes.
4. Stay within the task. Report related gaps separately. Do not fix them without permission.
5. Check the user's experience. Through the supported interfaces, check that every item was handled, and check the saved state, what the screen shows, failures, and recovery.
6. Report evidence and limits. Say what changed, which checks ran, and what is still open. A passing unit test does not prove the whole interaction works.
7. Keep held-out evidence outside development, following [Check 6.9](#check-6-9).

### Report

Report one row per applicable check and interface:

| Check | Interface | Result | Implemented | Tested | Missing |
| --- | --- | --- | --- | --- | --- |
| [3.1](#check-3-1) | Command line | Fail | Save path and code location | Test command and observed failure | Partial-write rollback |

Use Pass, Fail, Not run, or Not applicable, with a reason for the last two. Keep
implementation evidence separate from tests actually run. Record untested behavior as
untested, and list findings outside the task separately for the team to consider.

### Security scope and evidence

Include the test harnesses and stored evidence in the deployment review; see
[Assess test harnesses and deployment risks](#assess-test-harnesses-and-deployment-risks).

<a id="working-with-this-guide"></a>

<a id="scope-the-handoff-and-the-report"></a>

## Acceptance checks

Check revision note — October 26, 2026: Added optional Checks 2.11–2.13 for applications
that retain personal context. Language clarified without changing existing requirements.
The October 19 revision remains in effect: Checks 1.7 and 1.10 apply to the adopted inspection
contract; 1.13 requires person-confirmed discard through application-owned controls;
2.9 applies to saved-calculation workflows; 3.7 follows the guard's declared decision rule;
6.9 treats held-out evidence as exposed when used in development. Existing IDs are retained.


### 1. Share capabilities across interfaces

<a id="check-1-1"></a>

<!-- builder: embedded,mcp -->
- Check 1.1 — Shared behavior. Find and run the same operation through each supported interface. Inspect the saved result and the feedback, then exercise the supported recovery action. Verify that each interface uses the shared behavior and enforces the permissions assigned to its caller.

<a id="check-1-2"></a>

<!-- builder: embedded,mcp -->
- Check 1.2 — Shared validation. Try invalid input and a failed save through each supported interface. Confirm stored data is unchanged and each error explains what the caller can correct or try next.

<a id="check-1-3"></a>

<!-- builder: embedded,mcp -->
- Check 1.3 — Adapter boundaries. Trace a capability through the code that connects each interface to it. Verify that each route calls the shared implementation for validation and changes to application data.

<a id="check-1-4"></a>

<!-- builder: embedded,mcp -->
- Check 1.4 — Purpose in the tool's description. Inspect the tool definitions actually delivered to each supported agent interface. Verify that they convey the user need, result, and limits, distinguish related operations, and preserve the shared capability's meaning.

<a id="check-1-5"></a>

<!-- builder: embedded,mcp -->
- Check 1.5 — Interfaces fit their callers. Trace one user job through screen controls, agent actions, and command-line commands where supported. Include a read, an editor-opening request, and a supplied-content update: only the last may change stored content. Verify that each interface applies the same rules for which records the operation affects, how inputs are validated, and how changes can be recovered.

<a id="check-1-6"></a>

<!-- builder: embedded,mcp -->
- Check 1.6 — Screen actions fit the caller. Inspect the tool listing served to each interface. By default, screen actions must be absent from callers that do not share the user's screen, and rejected if invoked by name, while remaining available to the embedded agent. Where an external chat app is offered screen actions, verify that they work through that interface and that the agent uses them only when the user explicitly asks. Test both cases.

<a id="make-the-capability-registry-inspectable"></a>

Checks 1.7–1.11 apply when adopting portable inspection. Agree which records and interfaces
matter to the application, then verify that design. The
[inspection appendix](../reference/inspection.md) provides an example format to adapt.

<a id="check-1-7"></a>

<!-- builder: mcp -->
- Check 1.7 — Inspectable catalog. Export the agreed catalog and validate its chosen fields, unique IDs, versions, schemas, and handler bindings. Verify that screen controls and agent tools resolve to the same registered owner. Change a description and confirm the catalog revision changes.

<a id="check-1-8"></a>

<!-- builder: mcp -->
- Check 1.8 — Offered versus executed. Capture a real model request and verify its recorded list of offered tools matches the definitions actually delivered. Follow a resulting tool call to its resolved application action. Verify actions taken directly through screen controls are observable without fabricated model-call IDs.

<a id="check-1-9"></a>

<!-- builder: mcp -->
- Check 1.9 — Records match what happened. Exercise success, validation rejection, policy denial, handler failure, cancellation, and partial or uncertain effects where supported. Compare observations with actual state. Interrupt execution and verify an incomplete trace is not labeled successful; fail the exporter and verify a committed write is not retried.

<a id="check-1-10"></a>

<!-- builder: mcp -->
- Check 1.10 — Portable inspection. Read the adopted catalog, coverage description, and observations through an independent consumer without importing application handlers. Follow local and MCP calls where supported, recognize coverage gaps, and verify redaction occurs before export. Inspection access must not grant permission to invoke or replay actions.

<a id="check-1-11"></a>

<!-- builder: mcp -->
- Check 1.11 — Protected observation. Verify that instrumentation alone exposes no public inspection endpoint and captures no unauthorized content. Test catalog and trace access across app, user, and workspace boundaries, collector credential scope, redaction before export, and configured retention and deletion. Confirm that malicious instructions in a recorded result, and an observer's request to grant itself access, cannot authorize debugging actions. Verify that every recorded conversation says so to the person in it, including a tester typing into a simulated user's conversation, and that production conversations reach the trace store only under a separate, explicit decision.

<a id="check-1-12"></a>

<!-- builder: -->
- Check 1.12 — Tools for repeated jobs. From test results and use, list the jobs users ask for again and again that the agent does by combining general tools. Where one does not perform as well as you need, consider a tool made for that job, as general as the job allows (merge any two or more items, not one pair). If one is added, keep the general tools, and rerun the whole suite (Check 4.5).

<a id="check-1-13"></a>

<!-- builder: embedded -->
- Check 1.13 — Screen actions run through the application's own state. Verify agent screen actions use application-owned navigation and controls, and that the visible screen and recorded state agree. Verify directions come from the actual controls. Navigate with a partial edit present: preserve the draft where supported; if leaving would discard it, require the person's confirmation before navigating. Test canceling and confirming, and verify the agent cannot supply that confirmation.

<a id="check-1-14"></a>

<!-- builder: mcp -->
- Check 1.14 — Views supplement a complete text answer. MCP Apps lets a chat app display an interactive view supplied by an application's MCP server. The tool must also provide a complete text answer for chat apps that cannot display the view.

  Test the tool through two client connections: one that announces support for views and one that does not. Verify that:

  - Only the client that announces support receives the view.
  - Both receive a text answer containing every figure shown in the view.
  - The text and view use the same code-produced data.
  - The text gives each figure's meaning, units, and date, and says when data is unavailable or out of date, as the view does.
  - When a view is supplied, the accompanying text tells the model to add useful interpretation rather than repeat what the view shows.

  Verify the resulting conversation in both clients; an instruction to avoid repetition does not prove that the model follows it. Also make the view fail to display in a client that announced support, and confirm the conversation still makes sense from the text answer alone.

### 2. Help users finish the job

<a id="check-2-1"></a>

<!-- builder: embedded -->
- Check 2.1 — Subject and task. Discuss a problem, then ask "open it so I can fix that." Verify the target, the destination, and the absence of unrequested changes.

<a id="check-2-2"></a>

<!-- builder: embedded -->
- Check 2.2 — Context corrections. Change selection and ask about "this one"; correct a prior request; try an ambiguous reference. Verify the agent acts when the context supports one reasonable reading, and asks when plausible readings would produce materially different results.

<a id="check-2-3"></a>

<!-- builder: embedded -->
- Check 2.3 — Complete scope. Request every member of a named list. Verify all intended records are handled on the first request and unrelated records are preserved.

<a id="check-2-4"></a>

<!-- builder: embedded -->
- Check 2.4 — Visible outcomes. Exercise a multi-step job and undo. Check saved state and every visible representation, then repeat with the result offscreen and unsaved edits present. Explain unfinished work without hiding the result or unexpectedly moving keyboard focus.

<a id="check-2-5"></a>

<!-- builder: -->
- Check 2.5 — Jobs in ordinary language. Express a real job several ways without naming controls or tools, including an exploratory question, an information request, a clear change request, and an ambiguous acceptance of two offers. Grade useful outcomes, appropriate reads or actions, and necessary clarification; do not require one prescribed tool sequence for every phrasing.

<a id="check-2-6"></a>

<!-- builder: -->
- Check 2.6 — Additive references. Request one action, then "the other event type too." Verify the agent keeps the earlier subject, adds the requested event type, handles every intended record, and preserves the earlier settings. Repeat after an unrelated turn and with several plausible subjects; clarify only when needed.

<a id="check-2-7"></a>

<!-- builder: -->
- Check 2.7 — Correction after a misunderstanding. Include an actual mistaken assistant response before a user correction. Verify the correction updates the original request rather than the mistaken substitute. Score resulting state or calculation, answer truthfulness, and task completion separately; record a lost reference or metric substitution as a failure reason. Do not grade exact wording.

<a id="check-2-8"></a>

<!-- builder: -->
- Check 2.8 — Reference evidence and boundaries. Resolve a returned object, then exercise an expired or missing reference, a stale or deleted object, changed selection, a cross-workspace identifier, a failed write, and references that could identify more than one item. Verify scope and current permissions, refresh values when required, and never treat a proposed or rejected action as committed. Export only policy-permitted reference evidence.

<a id="check-2-9"></a>

<!-- builder: -->
- Check 2.9 — Revise a named result without changing the original. Where the application supports saved, revisable calculations, revise a computed result by its explicit ID and changed inputs. Verify unchanged inputs and original dated source data are preserved, the original result is untouched, a new result ID is returned, and all constraints are revalidated. Test invalid changes and missing, expired, or inaccessible IDs; never fall back to the latest result. Confirm that describing, referencing, or revising a hypothetical plan does not execute it or save it as a user setting.

<a id="check-2-10"></a>

<!-- builder: -->
- Check 2.10 — Familiar forms, documents, and spreadsheets. For a job whose data lives in a familiar form, document, spreadsheet, or calendar, have the agent make a change. Verify the change lands in the form, document, or spreadsheet itself, appears the way it already shows changes, and passes its own validation. For a review task, verify the item under review stays primary on screen, the decision is made only through the screen's controls, and the agent points to evidence rather than recommending a verdict unless asked.

#### For applications that retain personal context

Checks 2.11–2.13 apply when the application learns and saves information about the person.
Use [Learn about me](../guide/onboarding.md) to decide which information the assistance needs.

<a id="check-2-11"></a>

<!-- builder: -->
- Check 2.11 — Accurate personal context. State a clear fact, a tentative wish, a conditional goal, and a preference limited to one item or occasion. Verify saves follow the application's authorization policy and preserve the statement's uncertainty, conditions, and scope. Confirm the person can inspect, correct, and remove the information, receives confirmation when a save is not otherwise visible, and can undo it where supported. Verify later assistance uses the corrected information and no longer relies on removed facts.

<a id="check-2-12"></a>

<!-- builder: -->
- Check 2.12 — Current personal context. Give the application an old saved fact and compare requests that depend on it with requests that do not. Verify code supplies the last-confirmed date and elapsed time, and the agent checks relevance rather than treating elapsed time as proof of change. Confirm an answer that leaves the fact unchanged can update its confirmation date, while a correction updates the fact. Verify later assistance receives the current information.

<a id="check-2-13"></a>

<!-- builder: -->
- Check 2.13 — Relevant questions and remembered answers. Test missing facts that would help the current task alongside unrelated gaps. Verify the agent uses known information, asks only for the precision needed, and continues helping with the task. Include answers, refusals, and requests to stop questions in longer conversations. Check that questions do not repeat without new evidence or another review condition defined by the application, and verify any setup-question limits and stop/resume controls.

### 3. Enforce permissions, approval and recovery in code

<a id="3-enforce-the-safety-line-in-code"></a>

<a id="check-3-1"></a>

<!-- builder: embedded -->
- Check 3.1 — Atomic outcomes. Fail a single operation's save and retry a completed request. Verify that a failed save leaves stored data unchanged, retrying a completed request preserves the original result without applying the change again, and each reply reports what actually happened.

<a id="check-3-2"></a>

<!-- builder: embedded -->
- Check 3.2 — Recovery. Undo and redo a change. Verify the affected state and visible views; introduce an intervening edit and confirm recovery does not silently overwrite it.

<a id="check-3-3"></a>

<!-- builder: embedded,mcp -->
- Check 3.3 — Enforced authority. Call a forbidden operation directly and through every supported interface. Verify execution rejects it independently of prompts and tool listings.

<a id="check-3-4"></a>

<!-- builder: embedded,mcp -->
- Check 3.4 — Approval applies to this exact change. For actions requiring approval, try none, approval claimed in agent text, and changed proposal details, including consequential reversible actions and an interface without an approval channel. None may bypass the gate.

<a id="check-3-5"></a>

<!-- builder: -->
- Check 3.5 — Combined impact. For an operation that needs approval at scale, verify that the agent has an operation that takes one item or many, whose approval rule sees the whole change, and report any path where repeated single-item calls reach the same result without approval.

<a id="check-3-6"></a>

<!-- builder: embedded,mcp -->
- Check 3.6 — Data and resource boundaries. Place hostile instructions and prohibited data in inputs and stored records. Verify prohibited data is filtered before a model request and application permissions reject actions requested by hostile instructions. Exhaust call, time, cost, and retry limits; verify execution stops at the configured limit and reports what completed.

<a id="check-3-7"></a>

<!-- builder: -->
- Check 3.7 — Guards. For each guard, record its question, evidence, answer format, decision rule, and refusal behavior. Test the declared answer that permits the action: some guards ask whether an action is appropriate (yes permits it), while others ask whether a problem is present (no permits it). Where a guard returns a probability, test values on both sides of its threshold and exactly at the boundary. Measure false refusals and missed problems against independently labeled cases, and compare behavior with and without the guard. Verify invalid or unavailable required answers stop the protected action. Use the [todo app declarations and tests](../guide/authority.md#two-guard-questions-from-todo) as examples.

<a id="check-3-8"></a>

<!-- builder: mcp -->
- Check 3.8 — Audit record. Run turns that apply, refuse, and fail a change, and one where a review rewrites the reply. Verify one record per attempted change with its outcome and the checks that decided it, one record per reply with the text the user saw where the capture policy includes it and a mark that it was left out where it does not, and undo and redo recorded as new records that leave earlier records unchanged. Verify an evaluation compares each turn's records with what actually happened. Where the records go and how long they are kept is set in logging configuration, not in code.

<a id="check-3-9"></a>

<!-- builder: mcp -->
- Check 3.9 — Undo scope. Have the embedded agent change a field, then use the general Undo command; verify it reverts that change and names it. Have an external client change a field; verify the general Undo leaves it alone, that it does not clear the user's Redo, and that it can still be reversed from the change history.

<a id="check-3-10"></a>

<!-- builder: -->
- Check 3.10 — Uncertain outcomes. Let a change be saved and drop its reply before the caller receives it. Retry the request and verify that the change is applied once, that the retry returns the first outcome, that each attempt is recorded with its own identifier and both with the change's identifier, and that until the outcome is known the user is told the change is pending, not that it failed.

<a id="check-3-11"></a>

<!-- builder: -->
- Check 3.11 — Stopping a request. Stop a request of several changes after the first is saved and before the second starts. Verify that the second does not run, that nothing is left half-saved, that the first stays saved and can be undone, and that the user is told which changes were saved and which were not.

### 4. Give the model clear tools and current evidence

<a id="check-4-1"></a>

<!-- builder: embedded -->
- Check 4.1 — Relevant reads. Verify that data questions make relevant reads, navigation follow-ups avoid unrelated reads, and general explanations need no application data. Expose failed reads without inventing facts.

<a id="check-4-2"></a>

<!-- builder: embedded -->
- Check 4.2 — Current evidence. Change a quantity between turns; verify the next factual answer reads it. Change a summary's source data and verify source dates and staleness are communicated.

<a id="check-4-3"></a>

<!-- builder: embedded -->
- Check 4.3 — Delivered history. Rewrite an answer through review, fail an action, then continue the conversation. Verify history reflects the delivered answer, the actual outcome, and the current selection.

<a id="check-4-4"></a>

<!-- builder: embedded -->
- Check 4.4 — Application-written text. List the answer text the application can produce itself: save confirmations, directions to a setting, calculated results, the old and new place of a moved item, pending approvals. Verify the application shows each one as its own text and the model supplies only the choice (the destination, the operation, whether to ask). Confirm no prompt or tool description asks the model to repeat such text.

<a id="check-4-5"></a>

<!-- builder: evaluation -->
- Check 4.5 — Whole-suite rerun. After adding a capability, changing a tool description or result text, reordering tools, or adding a prompt sentence, run every case, not only the ones the change was meant to fix. Compare per-case results with the previous run and investigate any case that dropped, including cases unrelated to the change. Fix the tool description or result a drop exposes rather than the tool order. When the suite is too slow or costly to run in full after every change, run the cases closest to the change each time and the full suite before each release, and say in the report which was run.

<a id="check-4-6"></a>

<!-- builder: embedded -->
- Check 4.6 — One current copy. Where data goes with every message, hold a conversation of ten or more turns that changes that data, and read what the model received on the last turn. Confirm it holds one copy of the data, the current one.

### 5. Explore with simulated users

<a id="5-explore-with-persona-driven-users"></a>

<a id="check-5-1"></a>

<!-- builder: evaluation -->
- Check 5.1 — Credible scenarios. Inspect persona starting data, goals, and private backstory. Check plausibility with human observations; do not treat simulations as evidence of customer demand.

<a id="check-5-2"></a>

<!-- builder: evaluation -->
- Check 5.2 — Adaptive exploration. Run varied personas and adversarial inputs. Verify the simulated user responds to what actually happens, including refusals and errors. Set turn, time, and spending limits, verify that the test runner enforces them, and inspect the saved transcript, tool calls, errors, and state changes.

<a id="check-5-3"></a>

<!-- builder: evaluation -->
- Check 5.3 — Preserved failures. Reproduce a real-user or persona failure from saved starting state. Keep a fixed regression scenario alongside continued exploratory runs.

<a id="check-5-4"></a>

<!-- builder: evaluation -->
- Check 5.4 — Actions available to simulated users. List the actions the persona test runner lets the simulated user take. Each must be one the person could take on the screen (typing, clicking a visible control such as Approve or Deny). Try an action the person could not take, such as approving a request with no approval control shown, and confirm the test runner neither performs it nor records it as done.

### 6. Evaluate the user's outcome

<a id="check-6-1"></a>

<!-- builder: evaluation -->
- Check 6.1 — Outcome evidence. Check a conversation that sounds successful but misses part of the task. Verify evaluation catches the saved-state gap and records the extra questions, corrections, or manual steps the user needed to finish it.

<a id="check-6-2"></a>

<!-- builder: evaluation -->
- Check 6.2 — Judge calibration. Compare model judgments with labels of the same evidence. State who made the labels: a person, or an agent whose labels a person sampled and decided. Investigate disagreements and report review failures as unavailable rather than as passes or failures. For each judge that is asked more than once, show from the labeled set that taking the majority of several answers improves agreement; a judge whose errors repeat is asked once.

<a id="check-6-3"></a>

<!-- builder: evaluation -->
- Check 6.3 — Comparable runs. Compare versions using fixed starting data and criteria. Record model, prompt, tools, costs, response time, and individual failures; report exploratory runs separately.

<a id="check-6-4"></a>

<!-- builder: evaluation -->
- Check 6.4 — Tool independence. Stop the observability platform and run a suite. The same report and exit code must result, and the report must say what was and was not recorded. Where cases are pushed to the platform, edit one case in the platform's interface and confirm the next run refuses with a conflict rather than measuring the edited case.

<a id="check-6-5"></a>

<!-- builder: evaluation -->
- Check 6.5 — Served model. Read back a run and confirm every generation records the model that served it. Request an alias and confirm a dated snapshot, where the provider uses one, appears in the record; request a dated snapshot and confirm a different served model is flagged. Where the provider does not report which version served the call, confirm the record says so instead of repeating the requested name.

<a id="check-6-6"></a>

<!-- builder: evaluation -->
- Check 6.6 — Checks protect outcomes. For each check in a suite, name what it protects: trust, a policy requirement, or completion of the job. Run a correct answer phrased differently from the expectation and confirm no check fails it on wording alone. Confirm a check that fails good answers is retired and replaced, not edited in place.

<a id="check-6-7"></a>

<!-- builder: evaluation -->
- Check 6.7 — Grade only model-written text. For each check that reads answer text, mark whether that text is written by the model or by code. A check that grades the model's restatement of code's text is a design finding: move the text to the application (Check 4.4) and grade the choice or the state in code. Confirm judges read only model-written text, and that application-written text is marked so they can tell the difference.

<a id="check-6-8"></a>

<!-- builder: evaluation -->
- Check 6.8 — Grader assignment. For each check in a suite, name its grader: code, a model judging one specific criterion (a narrow judge), a model assessing the overall conversation (a broad judge), or a person. Flag any judge deciding something code can compute (state, arithmetic, identifiers, the destination chosen) and any agent-written figure the application could have computed. Confirm persona agents and models giving second opinions provide exploratory feedback, not pass or fail.

<a id="check-6-9"></a>

<!-- builder: evaluation -->
- Check 6.9 — Unseen cases for the same kind of task. For each case found in use or by a persona, find a held-out case for the same job with different items and words, written by someone other than the person making the fix, or by a separate session whose cases the fixing session cannot read. Confirm the tooling refuses to run it during fixing unless asked explicitly. Develop the fix against the visible cases. Stop changing it before running the held-out cases. Confirm that no fix, description, or example copies a held-out case's items or phrasing; vocabulary of the job that any user would use is expected to be shared. A held-out case may already pass before the fix; record that as a result. Keep held-out case contents and detailed results outside the development process. Once that evidence is used to diagnose or improve the system, move the case into the visible set and replace it. Running a held-out case without reading its contents or results does not use it up. The same applies when an automated optimizer, rather than a person, searches over prompts or tool descriptions.

<a id="check-6-10"></a>

<!-- builder: evaluation -->
- Check 6.10 — Reliability across attempts. For jobs where consistency matters, report pass^k, the estimated probability that all k attempts at the same job succeed, beside the pass rate. State k, the number of attempts, and how the estimate was calculated. Confirm the report does not present a pass rate alone as how often a repeated job succeeds.

<a id="check-6-11"></a>

<!-- builder: evaluation -->
- Check 6.11 — Injected failures. Run the suite with read failures, write failures, and timeouts injected. Confirm truthful reporting and complete recovery, and compare pass rates and pass^k with the clean run.

<a id="check-6-12"></a>

<!-- builder: evaluation -->
- Check 6.12 — Wording borrowed from test cases. Review tool names, descriptions, fixed lists of choices, and messages for wording that matches a test case or a reported conversation. Try each with a request nobody has used before. Remove wording that serves only one case, and rerun the suite.

<a id="check-6-13"></a>

<!-- builder: evaluation -->
- Check 6.13 — One place to see what happened. From a failed result, open the conversation as a developer and as a coding agent. Both must reach the same record: what the model was sent, the tools it called and what they returned, the state after each turn, and each check's verdict.

<a id="check-6-14"></a>

<!-- builder: evaluation -->
- Check 6.14 — Release decision. Before a release run, confirm a written rule names who decides, the failures that block the release, the failure rate accepted for the rest, and what makes a run inconclusive, such as ungraded judgments or a required check that did not run. Confirm the report applies the rule as written and gives cost and time for each completed job as well as for each model call.

<a id="check-6-15"></a>

<!-- builder: evaluation -->
- Check 6.15 — Experiment records. Pick an improvement a report claims and follow its link to the experiment record. Confirm the record gives the change, the model and application versions, the cases and the number of attempts, the grading criteria, the result, and what the experiment could not show.

### 7. Put the principles to work

These checks make the working rules reportable for the assigned integration task.

<a id="check-7-1"></a>

<!-- builder: embedded -->
- Check 7.1 — Scoped integration. Trace one assigned job before and after integration. Verify preserved behavior, shared execution, feedback, and recovery through existing and agent interfaces.

<a id="check-7-2"></a>

<!-- builder: embedded -->
- Check 7.2 — Bounded delivery. Report in-scope gaps against check IDs. Keep unrelated improvements separate; do not add interfaces, redesign the application, or change policy without task authorization.

## Evaluation infrastructure

The following implementation guidance supports the [evaluation method](../guide/evaluation.md).
It provides background for Checks 6.2–6.5 and 6.13–6.15 rather than a second checklist.
Select the infrastructure that fits the application and record any additional acceptance
criteria the team adopts.

Keep cases, graders, starting data, and result records in the repository. Send copies to the observability platform in one direction only: a case edited in the platform's interface blocks the next run with a conflict instead of silently changing what was measured. If the platform is stopped, every evaluation still runs and writes the same report; only the shared view is lost (Check 6.4). Keep the number of modules that import the platform's SDK small, so switching to another platform changes the recorder, the dataset transfer, and the links a results page writes, and nothing else.

Define the suite in the repository. Tracing tools organize evidence using concepts such as datasets, runs, sessions, and traces. A team thinks in suites: the cases, the grader and its exact version, the starting data, the spending cap, what triggers a run, and where the report goes. Write that definition once and derive every name the platform sees from it. Define the terms the team uses: an *experiment* compares two or more configurations that differ in one thing; a *run* is one execution of the selected cases and attempts.

Retire a case instead of editing it. A dataset file carries its active cases and a retired list mapping each retired case to its reason. Pushing archives the hosted copy under its own identity; a corrected case joins under a new one. A case listed as both active and retired is an error at load.

Record what actually served the call. A model name is often an alias the provider can move to a new snapshot without notice. Capture the model requested, the version the provider reports serving (or that it reported none) on every generation, and the application's commit on every run (Check 6.5). Choose deliberately between a pinned version and an alias the provider moves: an alias picks up the provider's changes without a release of the application, and a pinned version keeps the selected model version fixed until you change it. Where stable behavior matters, evaluate a new version before moving production to it.

Ask for a structured verdict. When a model's entire output is a decision, request a reply in a format the API enforces rather than JSON embedded in prose, and give a simulated user a field to say it is finished rather than a keyword the code searches for. A reply that cannot be read is *unavailable*, never zero and never a failure.

Build narrow checks as data. A fabrication check is a question, a feedback template, and the cases it must flag and the cases it must accept. Measure each question's rate of yes answers on deliberately introduced failures and valid answers before using it to check replies. Ask each question once unless calibration shows its errors vary between attempts; only then vote, asking until a majority is settled (two agreeing answers settle a three-vote check). A judge whose errors repeat gives the same wrong answer every time it is asked. Let code merge the verdicts. Record each check's vote and quoted evidence in the trace, under the review it belongs to.

Keep every review's reasons in the record. A review that a later review supersedes must keep its verdict, its flags or failed checks, and its feedback, and every review and rewrite must be recorded, with its text and feedback where the capture policy permits and a mark that the content was left out where it does not. Many observability backends serve verdicts through their APIs but not span contents, so the run report has to carry the reasons itself.

Give people a results page. Generate a results page from the run reports, never by hand. Name each evaluation by the question it answers, count results by conversation with the failed checks in plain words beneath, link each conversation to its trace, show a short history per evaluation, and put an outline of what happened (the request, the reads, the writes and any refusal, each review's verdict and reason, the answer) under each failed conversation. A link from a failure must open a page that shows the failure.

Read the prompt the model received. Traces show the request exactly as it left the application. Read them: they reveal formatting mistakes in instructions, rubrics that quote their own test cases and so can never fail them, and calls to interfaces the vendor has deprecated.

## Make references part of the capability contract

Preserve enough context to resolve conversational references: the person's original words,
recorded actions and results, and relevant application state. The model interprets the
reference; application code validates and executes the requested operation.

For workflows that need stored calculations or grouped actions, adapt the
[result-reference example](../reference/conversation-references.md) and Checks 2.8–2.9.
The `based_on` and `changes` fields are one possible interface for revising saved inputs.

## Assess test harnesses and deployment risks

Include persona runners, evaluators, debuggers, and data collectors when assessing security
risks to the system. A runner that simulates a user may still hold real provider credentials, invoke write capabilities, send context to external services, and save sensitive artifacts; putting data in a test directory does not isolate the process from other files or services. For each mode (without an interface, interactive, or connected to a live service), document the identities and credentials used, permitted data and destinations, control endpoints, capture policy, persistence and cleanup, and resource limits. Separate synthetic tests from explicitly authorized live tests.

Report the evidence and its limits, and make no assurances. These principles are engineering guidance, not a certification, a complete threat model, or a guarantee of security, privacy, regulatory compliance, or fitness for a purpose. A passing test establishes only the behavior observed under its recorded conditions. Avoid claims such as "secure" or "fully isolated" based on adopting this architecture. Each organization must assess its own deployment, data, integrations, and obligations, and this guide does not replace qualified security, privacy, or legal review.


Scope. Multi-user isolation, concurrent edits, network operation, and detailed cost forecasting need their own designs and tests; shared contracts help organize that work but do not solve it.

The inspection appendix links its supporting sources; the complete bibliography is in
[Sources and further reading](../reference/sources.md).
