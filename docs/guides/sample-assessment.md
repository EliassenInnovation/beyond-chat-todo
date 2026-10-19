# Todo sample review against Beyond Chat

Reviewed against Beyond Chat Implementation Guide 3.5-draft, October 15, 2026. Application baseline: `ecb27ead061d49c6d95e924f2dfb1c1dbf857dfc`. This assessment includes the accompanying uncommitted review fixes.

The sample is useful for learning shared operations, execution-time authority, current context, undo, and evaluation. It is a local, single-user teaching application. Its strongest evidence is deterministic tests of those boundaries. It is not a complete reference implementation of all 62 checks.

## Changes made in this review

| Problem | Resulting behavior | Regression evidence |
| --- | --- | --- |
| A batch saved one item at a time and could leave a partly applied action after a write failure. | Registered actions commit once using a temporary file and atomic replacement; failures restore memory. UI changes include their undo entry in the same transaction. | `test_failed_batch_save_restores_memory_and_file`, `test_batch_commits_once_and_click_includes_undo` |
| Tool results retained references to mutable tasks; later edits could rewrite earlier evidence. | Execution returns a detached result. | `test_tool_evidence_does_not_change_after_later_writes` |
| A pending deletion followed renamed or otherwise changed task details. | Approval checks the original task details, including after reload; stale and legacy proposals require renewal. | `test_approval_is_bound_to_requested_details_after_reload`, `test_legacy_approval_without_snapshot_requires_new_request` |
| Provider failure after a saved action skipped turn completion and undo. | The agent reports saved receipts, records the delivered fallback in history, and preserves undo. Unexpected failures also finalize recovery. | `test_provider_failure_preserves_saved_work_undo_and_history` |
| A missing truthfulness judge could still produce a pass, including on the HTML page. | Every required check must answer; missing evidence is inconclusive unless another check already failed. Individual verdicts and reasons are retained. | `test_each_required_judge_is_needed_for_a_pass`, page outcome tests |
| A full run could include held-out cases without an explicit request. | Ordinary runs exclude held-out cases; explicit selection still requires `--held-out`. | `test_default_suite_excludes_held_out_cases` |
| A misspelled policy could reach the handler. | Registration rejects unknown policy decisions and noncallable handlers. | `test_unknown_policy_is_rejected_at_registration` |
| Opening the app required a model key; setup assumed the author's machine and could borrow another project's credentials. | Model client creation is deferred until chat. Setup creates a local environment without editing shell profiles. Only this project's configuration is loaded. | `test_no_provider_key_needed_until_chat`, existing environment precedence tests |

Tests above are in [tests/test_reference.py](../../tests/test_reference.py) unless noted. Existing regression tests remain in [tests/test_main.py](../../tests/test_main.py), [tests/test_app.py](../../tests/test_app.py), and [tests/test_personas.py](../../tests/test_personas.py). The tool schemas, descriptions, and ordering are unchanged. The review changes failure handling, proposal validation, persistence, and reporting; it does not establish improved model selection accuracy.

## How to read the assessment

This table preserves the earlier review against its stated check definitions. The guide's
October 19 reconciliation makes optional inspection and saved-calculation designs explicit
and revises several checks. The historical results below have not been rerun or relabeled.
In particular, gaps against the proposed inspection export format are gaps against that
example contract, rather than a requirement for every application to adopt it. Agree on the
applicable checks before using this table as a template for another application.


**Pass** means the stated portion of the check was exercised with the evidence given. **Fail** means a required part is absent or contradicted by the code, even if other parts work. **Not run** means implementation or historical evidence exists but the acceptance scenario was not established in this review. **Not applicable** names a feature the sample does not offer. UI tests use Streamlit AppTest and the real component adapter; they do not establish every browser interaction.

The [walkthrough](walkthrough.md) follows real application paths and explains their limitations. These links identify the main evidence:

- [Registry and execution](../../todo/capabilities.py), [domain and storage](../../todo/todos.py), [view state](../../todo/view.py).
- [Agent loop](../../todo/agent.py), [screen adapter](../../todo/todo_view.py), [screen](../../todo/app.py).
- [Evaluation definitions and records](../../evaluations/evals.py), [judges](../../evaluations/judge.py), [report page](../../evaluations/evals_page.py), [calibration](../../evaluations/judge_calibration.py).
- [Tracing configuration](../../todo/langfuse_setup.py), [persona harness](../../evaluations/personas.py).

## Shared capabilities

| Check | Interface | Result | Implementation and tested evidence | Remaining limit |
| --- | --- | --- | --- | --- |
| 1.1 | UI and agent | Pass | Shared-owner, delete-policy and undo tests in `tests/test_main.py`; both adapters invoke `execute`. | Scope is these two adapters, not arbitrary clients. |
| 1.2 | UI and agent | Pass | Schema/domain validation and injected save-failure tests leave memory and disk unchanged. | JSON storage is single-process demo storage. |
| 1.3 | UI and agent | Pass | `test_the_screen_and_the_agent_reach_the_same_owner`; adapters translate rather than duplicate domain logic. | New adapters must preserve this path. |
| 1.4 | Agent | Not run | Action descriptions and exact tool order exist; schema equality checked against baseline. | No new paid measurement of description clarity. |
| 1.5 | UI and agent | Pass | `view.show` changes view state; registered todo actions change saved data; tests and offline walkthrough distinguish them. | No separate document editor or CLI adapter. |
| 1.6 | External clients | Not applicable | No MCP server or external-agent adapter. | Do not infer an external exposure policy from the embedded sample. |
| 1.7 | Catalog | Fail | Catalog exports identities, policies and schemas; duplicate IDs and revision changes tested. | Missing proposed contract fields including explicit result schemas, application version and support manifest. Its `presentation` effect name is older than the guide's `screen`. |
| 1.8 | UI and agent | Fail | Model requests and tool calls can be traced. | No unified UI invocation records or offered-tool snapshots joined to stable action identity. |
| 1.9 | UI and agent | Fail | Failure outcomes tested and tool errors recorded in agent traces. | No shared observation lifecycle for UI, cancellation, or uncertain effects. |
| 1.10 | Inspection | Fail | Catalog is serializable. | No complete independent inspection contract or support manifest. |
| 1.11 | Tracing | Not run | Export filter and visible recording indicator have local tests; sibling credential fallback removed. | Deployment access, retention, deletion and hostile trace tests not established. |
| 1.12 | Agent | Not run | Dedicated merge action and historical experiments exist alongside general tools. | No new paid whole-suite comparison. |
| 1.13 | UI and agent | Fail | Shared View and named actions; no synthetic mouse events. | Unsaved inline edits are not protected against a concurrent agent view change; directions remain model-written from screen descriptions. |
| 1.14 | MCP Apps | Not applicable | No MCP view transport. | The Streamlit component is not an MCP Apps view. |

## Helping users finish jobs

| Check | Interface | Result | Implementation and tested evidence | Remaining limit |
| --- | --- | --- | --- | --- |
| 2.1 | Agent | Not run | Pointing and control descriptions exist. | No fresh model evaluation of follow-up target selection. |
| 2.2 | Agent | Fail | Repeated conversations exercised ambiguity and follow-ups. | Some attempts dated or merged tasks before resolving the target; clarification remains fallible. |
| 2.3 | Agent | Fail | Batch validation tests pass; repeated conversations measured multi-item intent. | One attempt duplicated an already-combined task; intent selection is not consistently correct. |
| 2.4 | UI and agent | Fail | Saved-state and undo tests pass. | Full offscreen, focus, and unsaved-edit behavior is not implemented/tested. |
| 2.5 | Agent | Fail | Tell/show/do cases and shared view actions were exercised in evaluations. | Requests to email sometimes created an unwanted task instead. |
| 2.6 | Agent | Not run | Multi-turn additive cases exist. | No fresh paid run across distractors and ambiguous references. |
| 2.7 | Agent | Not run | Correction cases and separate state/claim/answer graders exist. | Actual model repair behavior not remeasured. |
| 2.8 | Agent | Fail | Stable task IDs and freshness checks tested within one in-memory list. | No workspace/reference evidence contract or cross-session freshness. |
| 2.9 | Computed plans | Not applicable | No immutable computed-result or hypothetical-plan feature. | Tasks are mutable records, not versioned calculation results. |
| 2.10 | UI and agent | Pass | Both adapters edit the same displayed task list through shared validation; AppTest and adapter tests. | No document-review decision workflow. |

## Execution and recovery

| Check | Interface | Result | Implementation and tested evidence | Remaining limit |
| --- | --- | --- | --- | --- |
| 3.1 | UI and agent | Fail | Atomic action persistence and rollback now tested. | Completed additions have no durable replay identity, so retries can duplicate them. |
| 3.2 | UI and agent | Pass | Undo/redo, intervening changes, reload and provider-failure recovery tested on the shared list. | No concurrency guarantee across separately loaded lists; irreversible deletion is explicit. |
| 3.3 | UI and agent | Pass | Direct forbidden calls refused; registry rejects malformed policy values; model arguments cannot choose actor. | Python callers are trusted application code, not authenticated remote clients. |
| 3.4 | UI and agent | Pass | Agent self-approval denied; changed task details and legacy proposals refused across reload. | No approval expiry or multi-user identity model. |
| 3.5 | Agent | Fail | Broad unselected bulk operations are person-only. | Repeated named single-item writes can reach broad impact; no cumulative approval threshold. |
| 3.6 | Agent | Fail | Step bound and structured tool validation exist. | No complete wall-time/cost budget, per-step call bound, or fresh adversarial-data assessment. |
| 3.7 | Declared semantic guards | Partial | The merge check and target/action checks run before writes. Guard inputs are declared, independent groups run concurrently, invalid answers refuse the invocation, and changed state is rechecked. | Fallible intent checks, not authorization boundaries. Target/action checks cover completion, dates, and deletion requests only; they are enabled by default, can falsely refuse valid requests, and still miss some ambiguous references. |
| 3.8 | UI and agent | Fail | Agent tool records and undo state exist. | Undo is not an append-only audit log; UI attempts and production outcomes lack complete durable records. |
| 3.9 | UI and agent | Pass | Shared UI/agent undo and redo tested, including attribution and deletion limit. | External-client behavior is not applicable. |
| 3.10 | UI and agent | Fail | Provider failure after a known save is reported. | No persisted operation/attempt IDs, deduplication receipts, or uncertain-outcome query. |
| 3.11 | Agent | Fail | Persona Play/Pause stops queued persona turns. | It does not cancel an active agent request between writes. |

## Tools and context

| Check | Interface | Result | Implementation and tested evidence | Remaining limit |
| --- | --- | --- | --- | --- |
| 4.1 | Agent | Not run | Current list supplied every turn; explicit read tool available. | Relevant action choice and failure response require paid evaluation. |
| 4.2 | Agent | Pass | Freshness and between-turn updates tested against the shared object. | Independent browser sessions can hold stale copies. |
| 4.3 | Agent | Pass | Delivered provider-error and step-limit replies enter history; previous tool results are detached snapshots. | There is no production rewriting pipeline. |
| 4.4 | Agent/UI | Pass | Application code delivers receipts directly; raw model explanations remain separate evaluation evidence. Regression tests cover omitted confirmations and incorrect model claims. | Model explanations can still be wrong and require evaluation. |
| 4.5 | Evaluation | Pass | Four complete 51-case runs and one incomplete run retained with fixed configuration and source snapshots. | This is visible-suite measurement, not a held-out result, release approval, or before/after efficacy comparison. |
| 4.6 | Agent | Not run | Existing tests verify replacement of the previous list while retaining user-change evidence. | Ten-turn acceptance trace not separately established. |

## Persona exploration

| Check | Interface | Result | Implementation and tested evidence | Remaining limit |
| --- | --- | --- | --- | --- |
| 5.1 | Personas | Not run | Distinct starting states and goals tested. | Plausibility needs human observation; simulations do not establish demand. |
| 5.2 | Personas | Not run | Bounded adaptive harness tests and a live three-turn Priya smoke test with checkpoints. | The smoke test ended at its turn limit; full exploratory-job acceptance and visible interaction remain unverified. |
| 5.3 | Evaluation | Not run | Pilot failures reproduce ambiguity and unwanted-task problems already covered by cases. | No new persona finding was independently confirmed and promoted to a regression in this follow-up. |
| 5.4 | Personas/UI | Pass | Tests restrict the harness to typing and available approval controls; separate test lists are separate. | Harness is a subset of human controls, not a full UI automation model. |

## Evaluating outcomes

| Check | Interface | Result | Implementation and tested evidence | Remaining limit |
| --- | --- | --- | --- | --- |
| 6.1 | Evaluation | Pass | Code graders tested on correct/incorrect outcomes and side effects; claims and completeness assessed separately. | Validates grader behavior, not current model success rates. |
| 6.2 | Judges | Not run | Labelled sets and calibration tooling exist; missing-judgment reporting corrected. | No new calibration or human-label review. |
| 6.3 | Evaluation | Pass | Source snapshots and hashes, package versions, fixed cases, model settings, per-call usage, and attempt execution time are recorded locally. Reports show supported-model cost estimates. | Prices are dated estimates, not invoices; unknown models or usage remain unknown. Source changes start a separate comparison period. |
| 6.4 | Evaluation | Pass | Real-provider fixed-suite runs and the Priya smoke test completed locally with trace export disabled. Local JSON and HTML retained results. | This proves operation without export, not outage behavior during an already-active export. |
| 6.5 | Model calls | Pass | Shared local instrumentation records requested and reported model names for agent, judge, and persona calls; absent identities remain null. | A reported alias does not establish an immutable provider implementation. |
| 6.6 | Graders | Fail | State/claim/answer tests exist. | Receipt repetition still grades model reproduction of application text. |
| 6.7 | Graders | Fail | `model_words` removes known receipts before claim judging. | Receipt repetition should be eliminated through direct rendering. |
| 6.8 | Graders | Pass | Code grades state/arithmetic; named model judges grade language; personas explore rather than assign pass/fail. | This is assignment evidence, not renewed judge calibration. |
| 6.9 | Evaluation | Fail | Explicit held-out selection enforced and default-run leak fixed. | Held-outs still live in a file the fixing agent can read; retirement and replacement are not automated. |
| 6.10 | Reports | Pass | Reports show repeated-attempt consistency alongside individual results; incomplete attempts cannot become passes. | Uses k equal to attempts per case, rather than arbitrary k. |
| 6.11 | Evaluation | Not run | Deterministic failure injection and save-failure tests pass. | No paid injected-versus-clean suite comparison. |
| 6.12 | Tool wording | Not run | Tool schemas unchanged in this review. | Independent wording audit with fresh requests not run. |
| 6.13 | Reports | Not run | HTML and JSON reports share conversation evidence; optional trace links. | Live trace access by both reviewer types not verified. |
| 6.14 | Release | Fail | Reports separate completeness, variation, and owner-specified acceptance criteria; attempt cost and execution time are available. | No owner-approved release thresholds or automated release gate. Statistical stability does not establish acceptability. |
| 6.15 | Experiments | Not run | Commit messages, frozen records and previous review notes retain experiment evidence. | Historical quantitative claims not all traced and independently reproduced. |

## Integration scope

| Check | Interface | Result | Implementation and tested evidence | Remaining limit |
| --- | --- | --- | --- | --- |
| 7.1 | UI and agent | Pass | Before/after regression suite plus explicit shared-path failure tests. | Browser gestures and live model reliability are separate evidence. |
| 7.2 | Repository | Pass | Changes focus on demonstrated defects, setup, reporting, review and walkthrough. | No MCP server, database replacement, publication, commit or push. |

## Publication preparation

The sample’s original code and documentation have an [MIT license](../../LICENSE).
Adapted TodoMVC styling has separate [CC BY 4.0 attribution](../../README.md#license).
This clean distribution excludes the original repository's presentation assets, author-machine
service scripts, credentials, saved personal todos, and raw local experiment records.
The curated offline evaluation example is included; it contains synthetic conversations.
The license does not grant trademark rights in company names or branding.

Prioritize follow-up work by consequence: durable retries and concurrent storage before remote use; active-request cancellation and budgets before longer jobs; production audit records before consequential workflows; direct receipt rendering before claiming model-independent confirmation delivery. The sample can be published as a bounded worked example with these limitations stated, rather than presenting each missing feature as already solved.

## Evidence and remaining limitations

The sample's offline tests exercise shared execution, permissions, approval binding,
persistence, recovery, UI context, guard orchestration, and evaluation reporting.
The current repository has 291 offline tests.

The latest full visible behavior run before the directory reorganization passed 51/51.
Forty repeated compound requests all created the requested deletion approvals, with no
guard refusals. The unchanged overall grading passed 34/40; reply completeness and
claim-grading concerns remain. These are development measurements, not a production
failure-rate estimate or an accepted control-chart baseline.

These measurements came from the development workspace; their full raw records are not
included in this starter. The [offline example](../../examples/evaluation-review/README.md)
provides a separate, inspectable collection for learning how to review results. Use the
[evaluation guide](evaluation-results.md) to measure your own configuration.
