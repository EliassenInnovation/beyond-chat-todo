# Todo sample review against Beyond Chat

Assessed October 25, 2026 against application commit
`1b4b3c2b5f62bbd7a2ee7e48e11ff85b3e8cd438` and all 62 acceptance checks in
[implementation.md](../principles/implementation.md), including its October 19 revision.
The working tree was clean when verification began. This page records the assessment;
application code was not changed during it.

The sample is a local, single-user teaching application. It demonstrates shared operations,
execution-time authority, current context, undo, and evaluation. Its strongest current
evidence is deterministic testing of those boundaries. It does not implement every check.

## How to read the assessment

**Pass** means the check was verified within the interface and scope stated in its row.
**Fail** means inspection or testing found a required part missing.
**Not run** means the acceptance scenario was not established in this review, even where
supporting implementation and offline tests exist. **Not applicable** identifies a feature
outside the sample. A model's fallibility alone is not a reason to mark a mechanism Fail;
its measured behavior and the check's requirements decide that result.

The catalog is assessed against the sample's declared contract, rather than every field in
the optional inspection appendix. The sample has no external-agent adapter, MCP Apps view,
portable observation consumer, saved calculations, or multi-user workspace. Rows name these
limits instead of treating them as implemented features.

Verification on the stated commit:

- `.venv/bin/python -m pytest -q`: **331 passed**, with seven Langfuse SDK deprecation warnings.
  Tests isolate local provider settings and use model stand-ins; they make no model calls.
- `python3 -m todo.walkthrough`: all five steps passed using disposable data.
- Code inspection of the registry, domain/storage, screen adapter, agent and guards,
  persona harness, usage accounting, graders and report generation.

No paid model evaluations, human judge calibration, real-browser interaction study, or
live tracing-service outage experiment was run. Earlier development measurements are not
fresh evidence for this commit. Streamlit AppTest checks the page and component inputs;
component events are tested through the real adapter, without browser gestures.

The [walkthrough](walkthrough.md) follows the application paths. Main evidence sources:

- [Registry and execution](../../todo/capabilities.py), [domain and storage](../../todo/todos.py), [view state](../../todo/view.py).
- [Agent loop](../../todo/agent.py), [screen adapter](../../todo/todo_view.py), [screen](../../todo/app.py).
- [Evaluation definitions and records](../../evaluations/evals.py), [judges](../../evaluations/judge.py), [report page](../../evaluations/evals_page.py).
- [Tracing configuration](../../todo/langfuse_setup.py), [persona harness](../../evaluations/personas.py), [token accounting](../../todo/model_usage.py).
- [Offline tests](../../tests/test_main.py), [recovery tests](../../tests/test_reference.py), [guard tests](../../tests/test_guard_check.py), [screen tests](../../tests/test_app.py).

## Shared capabilities

| Check | Interface | Result | Implemented | Tested or inspected in this review | Remaining limit |
| --- | --- | --- | --- | --- | --- |
| 1.1 | UI and agent | Pass | Shared-owner, delete-policy and undo tests in `tests/test_main.py`; both adapters invoke `execute`. | `test_the_screen_and_the_agent_reach_the_same_owner`; walkthrough. | Scope is these two adapters, not arbitrary clients. |
| 1.2 | UI and agent | Pass | Schema/domain validation and injected save-failure tests leave memory and disk unchanged. | `test_arguments_are_checked_before_the_handler_runs`; `test_failed_batch_save_restores_memory_and_file`. | JSON storage is single-process demo storage. |
| 1.3 | UI and agent | Pass | `test_the_screen_and_the_agent_reach_the_same_owner`; adapters translate rather than duplicate domain logic. | Shared-owner test in `test_main.py`; inspected both adapters. | New adapters must preserve this path. |
| 1.4 | Agent | Pass | Inspected the embedded tools built by `Registry.tools_for` from descriptions and declared facts in `todos.py` and `view.py`; tool membership and order tests pass. | Tool-order/membership tests in `test_main.py`; description inspection. | Description inspection does not establish model selection reliability. |
| 1.5 | UI and agent | Pass | `view.show` changes view state; registered todo actions change saved data; tests and offline walkthrough distinguish them. | `test_show_todos_changes_the_view_only`; walkthrough byte-for-byte save checks. | No separate document editor or CLI adapter. |
| 1.6 | External clients | Not applicable | No MCP server or external-agent adapter. | Scope inspection; no applicable execution scenario. | Do not infer an external exposure policy from the embedded sample. |
| 1.7 | Catalog | Pass | Assessed the sample catalog contract: identities, input schemas, handler bindings, policies, guard declarations and content-derived revision. Catalog and registration tests pass. | Catalog revision and duplicate-registration tests in `test_main.py` and `test_reference.py`. | The optional appendix format is not adopted wholesale; result schemas and a support manifest are not claimed. |
| 1.8 | UI and agent | Fail | Model requests and tool calls can be traced. | Inspected `Agent.run_tool`, `todo_view.apply` and `execute`. | No unified UI invocation records or offered-tool snapshots joined to stable action identity. |
| 1.9 | UI and agent | Fail | Failure outcomes tested and tool errors recorded in agent traces. | Failure/rollback tests in `test_reference.py`; inspected observation paths. | No shared observation lifecycle for UI, cancellation, or uncertain effects. |
| 1.10 | Inspection | Not applicable | The sample exposes a serializable registry catalog but does not adopt a portable observation/inspection interface. | Scope inspection; no applicable execution scenario. | An independent inspection consumer and coverage manifest are outside this sample. |
| 1.11 | Tracing | Not run | Tracing export filtering and a visible recording indicator are implemented. | Export-selection tests in `test_main.py`; recording-indicator tests in `test_app.py`. | Deployment access, retention, deletion and hostile trace tests not established. |
| 1.12 | Agent | Not run | Dedicated merge action and historical experiments exist alongside general tools. | Code inspection only; acceptance scenario not run. | No new paid whole-suite comparison. |
| 1.13 | UI and agent | Fail | Shared View and named actions; no synthetic mouse events. | View/adapter tests in `test_app.py`; inspected inline editor in `todo/assets/todo_view.js`. | Unsaved inline edits are not protected against a concurrent agent view change; directions remain model-written from screen descriptions. |
| 1.14 | MCP Apps | Not applicable | No MCP view transport. | Scope inspection; no applicable execution scenario. | The Streamlit component is not an MCP Apps view. |

## Helping users finish jobs

| Check | Interface | Result | Implemented | Tested or inspected in this review | Remaining limit |
| --- | --- | --- | --- | --- | --- |
| 2.1 | Agent | Not run | Pointing and control descriptions exist. | Code inspection only; acceptance scenario not run. | No fresh model evaluation of follow-up target selection. |
| 2.2 | Agent | Not run | Ambiguity, clarification-order and correction graders have offline tests; current-state context and guards are implemented. | `test_clarification_sequence.py`; guard orchestration tests. No live model run. | No fresh model conversations established context correction or clarification reliability. |
| 2.3 | Agent | Not run | Atomic multi-item validation and unrelated-field preservation have offline tests. | Batch and unrelated-field tests in `test_main.py` and `test_reference.py`. | No fresh model run established selection of every intended item on the first request. |
| 2.4 | UI and agent | Fail | Saved-state and undo tests pass. | AppTest and component-adapter tests; no real-browser focus/draft test. | Full offscreen, focus, and unsaved-edit behavior is not implemented/tested. |
| 2.5 | Agent | Not run | Tell/show/do tools and unavailable-capability grading exist. | Code inspection only; acceptance scenario not run. | No fresh model run across ordinary-language variants; historical failures are not current measurements. |
| 2.6 | Agent | Not run | Multi-turn additive cases exist. | Code inspection only; acceptance scenario not run. | No fresh paid run across distractors and ambiguous references. |
| 2.7 | Agent | Not run | Correction cases and separate state/claim/answer graders exist. | Code inspection only; acceptance scenario not run. | Actual model repair behavior not remeasured. |
| 2.8 | Agent | Not run | Stable todo IDs, stale-read refusal, missing-ID validation and failed-save recovery are tested. | Fresh-read tests in `test_main.py`; missing-ID/save-failure tests. | No full reference scenario was run; expiry and cross-workspace references are outside this single-list application. |
| 2.9 | Computed plans | Not applicable | No immutable computed-result or hypothetical-plan feature. | Scope inspection; no applicable execution scenario. | Tasks are mutable records, not versioned calculation results. |
| 2.10 | UI and agent | Pass | Both adapters edit the same displayed task list through shared validation; AppTest and adapter tests. | `test_screen_actions_use_the_list_operations`; shared-owner test. | No document-review decision workflow. |

## Execution and recovery

| Check | Interface | Result | Implemented | Tested or inspected in this review | Remaining limit |
| --- | --- | --- | --- | --- | --- |
| 3.1 | UI and agent | Fail | Atomic action persistence and rollback now tested. | Atomic save-failure tests; inspected absence of replay identity. | Completed additions have no durable replay identity, so retries can duplicate them. |
| 3.2 | UI and agent | Pass | Undo/redo, intervening changes, reload and provider-failure recovery tested on the shared list. | Undo/redo and reload tests in `test_main.py`; provider-failure tests in `test_reference.py`. | No concurrency guarantee across separately loaded lists; irreversible deletion is explicit. |
| 3.3 | UI and agent | Pass | Direct forbidden calls refused; registry rejects malformed policy values; model arguments cannot choose actor. | Direct forbidden-operation and unknown-policy tests. | Python callers are trusted application code, not authenticated remote clients. |
| 3.4 | UI and agent | Pass | Agent self-approval denied; changed task details and legacy proposals refused across reload. | Bound-approval/reload tests in `test_reference.py`; direct self-approval refusal. | No approval expiry or multi-user identity model. |
| 3.5 | Agent | Fail | Broad unselected bulk operations are person-only. | Impact-policy registration tests; inspected repeated-call execution. | Repeated named single-item writes can reach broad impact; no cumulative approval threshold. |
| 3.6 | Agent | Fail | Agent loop is bounded to eight steps. Persona CLI defaults to 100,000 tokens; eval CLI accepts a token allowance but defaults to none. Shared accounting includes guards and stops subsequent calls when usage is exhausted or unknown. Streamlit defaults to loopback. | Budget/unknown-usage tests in `test_persona_headless.py`; inspected runner defaults and `todo/model_usage.py`. | No complete prohibited-data filter or request-wide time/spending/retry budget. Ordinary chat has no token allowance; in-flight calls may exceed an allowance. Loopback binding does not supply those controls. |
| 3.7 | Declared semantic guards | Not run | Declared evidence, both decision polarities, probability boundaries, concurrent checks, state rechecks and unavailable-answer refusal have offline tests. | `test_guard_check.py`; merge-guard tests in `test_main.py`; native Boolean guard tests in `test_anthropic.py`. | Independent false-refusal/missed-problem measurement and a with/without-guard comparison were not rerun. Guard fallibility alone is not a failed acceptance check. |
| 3.8 | UI and agent | Fail | Agent tool records and undo state exist. | Inspected undo persistence and adapter/agent recording paths. | Undo is not an append-only audit log; UI attempts and production outcomes lack complete durable records. |
| 3.9 | UI and agent | Pass | Shared UI/agent undo and redo tested, including attribution and deletion limit. | Shared undo/redo tests and walkthrough. | External-client behavior is not applicable. |
| 3.10 | UI and agent | Fail | Provider failure after a known save is reported. | Provider-failure recovery tests; inspected persistence and execution. | No persisted operation/attempt IDs, deduplication receipts, or uncertain-outcome query. |
| 3.11 | Agent | Fail | Persona Play/Pause stops queued persona turns. | Queued-persona pause test in `test_app.py`; inspected agent loop. | It does not cancel an active agent request between writes. |

## Tools and context

| Check | Interface | Result | Implemented | Tested or inspected in this review | Remaining limit |
| --- | --- | --- | --- | --- | --- |
| 4.1 | Agent | Not run | Current list supplied every turn; explicit read tool available. | Code inspection only; acceptance scenario not run. | Relevant action choice and failure response require paid evaluation. |
| 4.2 | Agent | Pass | Freshness and between-turn updates tested against the shared object. | Between-turn/current-filter tests in `test_main.py` and `test_reference.py`. | Independent browser sessions can hold stale copies. |
| 4.3 | Agent | Pass | Delivered provider-error and step-limit replies enter history; previous tool results are detached snapshots. | Detached-evidence and fallback-history tests in `test_reference.py`. | There is no production rewriting pipeline. |
| 4.4 | Agent/UI | Fail | Code delivers operation receipts directly; tests verify delivery even with an empty or incorrect model explanation. The prompt says not to repeat receipts. | Direct-confirmation test in `test_anthropic.py`; inspected prompt and screen descriptions. | Directions to controls still come from model-written text; the check covers those as well as save confirmations. |
| 4.5 | Evaluation | Not run | Fixed-suite runner and comparison reports exist; offline regression suite was run. | Code inspection only; acceptance scenario not run. | No fresh paid whole-suite before/after comparison. Historical runs are not evidence for this commit. |
| 4.6 | Agent | Not run | Existing tests verify replacement of the previous list while retaining user-change evidence. | One-current-list test in `test_main.py`; ten-turn scenario not run. | Ten-turn acceptance trace not separately established. |

## Persona exploration

| Check | Interface | Result | Implemented | Tested or inspected in this review | Remaining limit |
| --- | --- | --- | --- | --- | --- |
| 5.1 | Personas | Not run | Distinct starting states and goals tested. | Persona starting-state tests; no human plausibility study. | Plausibility needs human observation; simulations do not establish demand. |
| 5.2 | Personas | Fail | Adaptive persona harness has turn limits, token accounting, interruption checkpoints and saved judgments; offline harness tests pass. | `test_persona_headless.py`, `test_personas.py` and visible-player AppTest tests. | No harness-wide time limit or hard spending cap, and no fresh live adaptive exploration. |
| 5.3 | Evaluation | Not run | Regression scenarios and saved persona records are supported. | Code inspection only; acceptance scenario not run. | No new persona finding was independently confirmed and promoted to a regression in this follow-up. |
| 5.4 | Personas/UI | Pass | Tests restrict the harness to typing and available approval controls; separate test lists are separate. | Persona click/approval and scratch-list tests in `test_personas.py` and `test_app.py`. | Harness is a subset of human controls, not a full UI automation model. |

## Evaluating outcomes

| Check | Interface | Result | Implemented | Tested or inspected in this review | Remaining limit |
| --- | --- | --- | --- | --- | --- |
| 6.1 | Evaluation | Pass | Code graders tested on correct/incorrect outcomes and side effects; claims and completeness assessed separately. | Grader good/bad fixtures and `test_clarification_sequence.py`. | Validates grader behavior, not current model success rates. |
| 6.2 | Judges | Not run | Labelled sets and calibration tooling exist; missing-judgment reporting corrected. | Calibration fixture-integrity tests; no new model calibration. | No new calibration or human-label review. |
| 6.3 | Evaluation | Pass | Configuration fingerprints, source hashes, package/model settings, usage, latency and separate persona records have offline tests. Reader-supplied rates retain their date; absent rates leave costs unknown. | `test_eval_monitor.py`, `test_model_rates.py`; guard-configuration fingerprint test. | Tests establish recording/comparison behavior with fixtures, not current model outcomes or actual provider charges. |
| 6.4 | Evaluation | Not run | Offline tests exercise disabled tracing and an unreachable-server app configuration; local run/report paths exist. | Unreachable/disabled tracing AppTest tests; no live platform-outage run. | No live suite with the platform stopped or exporter outage was run. Hosted case editing/conflict detection is not verified. |
| 6.5 | Model calls | Not run | Shared instrumentation records requested and returned model IDs separately; report tests distinguish changed and missing served IDs. | Requested/served metadata and comparability tests in `test_eval_monitor.py`; inspected `call_model`. | No live alias-versus-snapshot request was made in this review. |
| 6.6 | Graders | Not run | Correct/incorrect grader fixtures pass. `receipts_repeated` now checks delivery of code-written receipts, not model copying. | Offline grader fixtures; inspected receipt-delivery check. | No check-by-check outcome/wording audit or retirement-and-replacement exercise was completed. |
| 6.7 | Graders | Pass | `model_words` uses the saved raw `model_reply` for new records and strips known receipts in legacy records. Claims judges receive model text with delivered text retained as context; receipt delivery is checked in code. | `test_the_claims_judges_read_only_what_the_model_wrote`; direct-confirmation tests; inspected judge call sites. | Legacy receipt stripping is a compatibility heuristic; it cannot recover raw text that was never saved. |
| 6.8 | Graders | Pass | Code grades state/arithmetic; named model judges grade language; personas explore rather than assign pass/fail. | Inspected code/model grader assignment and persona findings; offline grader tests. | This is assignment evidence, not renewed judge calibration. |
| 6.9 | Evaluation | Fail | Explicit held-out selection enforced and default-run leak fixed. | Default/explicit held-out-selection tests; did not open held-out case bodies for this review. | Held-outs still live in a file the fixing agent can read; retirement and replacement are not automated. |
| 6.10 | Reports | Pass | Reports show repeated-attempt consistency alongside individual results; incomplete attempts cannot become passes. | Report tests in `test_main.py` and completeness tests in `test_eval_monitor.py`. | Uses k equal to attempts per case, rather than arbitrary k. |
| 6.11 | Evaluation | Not run | Deterministic failure injection and save-failure tests pass. | Injected-failure test in `test_main.py`; save-failure tests. No paid comparison. | No paid injected-versus-clean suite comparison. |
| 6.12 | Tool wording | Not run | Tool definitions are generated from registry declarations. | Code inspection only; acceptance scenario not run. | Independent wording audit with fresh requests not run. |
| 6.13 | Reports | Not run | Local JSON and HTML expose conversation, tools, states and judgments; report evidence integrity and HTML escaping tests pass. | `test_eval_collection.py`; report-page tests in `test_reference.py`. | Developer and coding-agent navigation to the same complete failed-run evidence was not exercised end to end. |
| 6.14 | Release | Fail | Reports separate completeness, variation, and owner-specified acceptance criteria; attempt cost and execution time are available. | Policy/completeness/chart tests in `test_eval_monitor.py`; inspected report policy. | No owner-approved release thresholds or automated release gate. Statistical stability does not establish acceptability. |
| 6.15 | Experiments | Not run | Commit messages, frozen records and previous review notes retain experiment evidence. | Code inspection only; acceptance scenario not run. | Historical quantitative claims not all traced and independently reproduced. |

## Integration scope

| Check | Interface | Result | Implemented | Tested or inspected in this review | Remaining limit |
| --- | --- | --- | --- | --- | --- |
| 7.1 | UI and agent | Not run | Shared-path regression tests and the five-step offline walkthrough pass on the assessed commit. | Full offline suite and `python3 -m todo.walkthrough`. | This documentation assessment made no application integration; a new before/after integration scenario was not run. |
| 7.2 | Repository | Pass | Assessment changes are limited to this page; implementation gaps are reported by check ID. | Reviewed this page diff against the fixed application baseline. | No application changes or new interfaces were made in this review. |

## Publication preparation

The repository's current [license](../../LICENSE) identifies it as an Eliassen Group
confidential draft with all rights reserved. An open-source license and public repository
remain publication decisions; this assessment does not grant permission to redistribute it.
Adapted TodoMVC styling has separate [CC BY 4.0 attribution](../../README.md#license).
The [curated evaluation example](../../examples/evaluation-review/README.md) contains
synthetic conversations and retains its historical grades. It is useful for learning to
review results, not a current acceptance run.

Prioritize follow-up work by consequence: durable retries and concurrent storage before
remote use; active-request cancellation and resource boundaries before unattended use;
and fresh model, grader and human review before making reliability claims. The checklist
builder helps record scope decisions; it does not supply acceptance evidence.
