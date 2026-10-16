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

Tests above are in [test_reference.py](../test_reference.py) unless noted. Existing regression tests remain in [test_main.py](../test_main.py), [test_app.py](../test_app.py), and [test_personas.py](../test_personas.py). The tool schemas, descriptions, and ordering are unchanged. The review changes failure handling, proposal validation, persistence, and reporting; it does not establish improved model selection accuracy.

## How to read the assessment

**Pass** means the stated portion of the check was exercised with the evidence given. **Fail** means a required part is absent or contradicted by the code, even if other parts work. **Not run** means implementation or historical evidence exists but the acceptance scenario was not established in this review. **Not applicable** names a feature the sample does not offer. UI tests use Streamlit AppTest and the real component adapter; they do not establish every browser interaction.

The [walkthrough](walkthrough.md) follows real application paths and explains their limitations. These links identify the main evidence:

- [Registry and execution](../capabilities.py), [domain and storage](../todos.py), [view state](../view.py).
- [Agent loop](../agent.py), [screen adapter](../todo_view.py), [screen](../app.py).
- [Evaluation definitions and records](../evals.py), [judges](../judge.py), [report page](../evals_page.py), [calibration](../judge_calibration.py).
- [Tracing configuration](../langfuse_setup.py), [persona harness](../personas.py).

## Shared capabilities

| Check | Interface | Result | Implementation and tested evidence | Remaining limit |
| --- | --- | --- | --- | --- |
| 1.1 | UI and agent | Pass | Shared-owner, delete-policy and undo tests in `test_main.py`; both adapters invoke `execute`. | Scope is these two adapters, not arbitrary clients. |
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
| 2.2 | Agent | Fail | The October 15 pilot exercised ambiguity and follow-ups. | Some attempts dated or merged tasks before resolving the target; see the pilot review. |
| 2.3 | Agent | Fail | Batch validation tests pass; the pilot measured multi-item intent. | One attempt duplicated an already-combined task; intent selection is not consistently correct. |
| 2.4 | UI and agent | Fail | Saved-state and undo tests pass. | Full offscreen, focus, and unsaved-edit behavior is not implemented/tested. |
| 2.5 | Agent | Fail | Tell/show/do cases and shared view actions were exercised in the pilot. | Requests to email sometimes created an unwanted task instead. |
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
| 4.4 | Agent/UI | Fail | Code generates receipts and grader distinguishes them. | `SAY_RECEIPT` still asks the model to repeat code text; direct rendering needs a separate measured change. |
| 4.5 | Evaluation | Pass | Four complete 51-case runs and one incomplete run retained with fixed configuration and source snapshots. | This is visible-suite measurement, not a held-out result, release approval, or before/after efficacy comparison. |
| 4.6 | Agent | Not run | Existing tests verify replacement of the previous list while retaining user-change evidence. | Ten-turn acceptance trace not separately established. |

## Persona exploration

| Check | Interface | Result | Implementation and tested evidence | Remaining limit |
| --- | --- | --- | --- | --- |
| 5.1 | Personas | Not run | Distinct starting states and goals tested. | Plausibility needs human observation; simulations do not establish demand. |
| 5.2 | Personas | Not run | Bounded adaptive harness tests and a live three-turn Priya smoke test with checkpoints. | The smoke test ended at its turn limit; full exploratory-job acceptance and visible interaction remain unverified. |
| 5.3 | Evaluation | Not run | Pilot failures reproduce ambiguity and unwanted-task problems already covered by cases. | No new persona finding was independently confirmed and promoted to a regression in this follow-up. |
| 5.4 | Personas/UI | Pass | Tests restrict the harness to typing and available approval controls; scratch lists are separate. | Harness is a subset of human controls, not a full UI automation model. |

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

The sample code and accompanying documentation have an [MIT license](../LICENSE).
This clean distribution excludes the original repository's presentation assets, author-machine
service scripts, credentials, saved personal todos, and raw local experiment records.
The curated offline evaluation example is included; it contains synthetic conversations.
The license does not grant trademark rights in company names or branding.

Before publishing, verify the chosen distribution and its Git history contain no credentials or private records; run a clean installation on a second environment; complete and record the visible model evaluation and judge calibration; and identify the owner and evidence required for a release. The code is updated locally, not published. The existing untracked `Claude outputs/` directory is outside this review.

Prioritize follow-up work by consequence: durable retries and concurrent storage before remote use; active-request cancellation and budgets before longer jobs; production audit records before consequential workflows; direct receipt rendering before claiming model-independent confirmation delivery. The sample can be published as a bounded worked example with these limitations stated, rather than presenting each missing feature as already solved.

## Verification for this revision

- macOS, the repository's existing Python 3.13 environment: **225 tests passed** (`python -m pytest -q`). This includes Streamlit AppTest, the existing talk-anchor tests, and 32 added regression cases.
- `python3 walkthrough.py`: all five offline examples completed and their assertions passed.
- Agent tool schemas, descriptions, and ordering compared byte-for-byte with the baseline: identical. Rechecked using default `json.dumps(agent.TOOLS)`: both HEAD and the revised code have SHA-256 `2caf2ed24081a1db2bb4600eef3ad0f8dad570dd9a8af97de8e325fcbb0308e7`.
- HTML report rendered in Chrome at 1350 px and 390 px widths; expanded evidence inspected and mobile horizontal overflow checked. Historical reports were used to inspect layout, not presented as new model results.
- All 62 check IDs appear once in this review. Walkthrough/review local links resolve. Python compilation and setup shell syntax checks pass.

The initial verification above preceded paid model evaluation and the monitoring additions. Subsequent verification and pilot results are recorded below. New judge calibration, extended persona exploration, and a public-release history audit remain separate work. Deterministic tests establish exercised code paths, not model reliability.

## Monitoring and persona follow-up

- Headless personas save partial sessions and offer an offline step-through review. Token
  allowances stop subsequent calls, not an in-flight response; they are not dollar caps.
- The visible player can be enabled independently of trace export. No Langfuse account or
  running service is required, although the Python SDK remains a dependency.
- Monitoring calculations have tests for missing/duplicate evidence, changed configurations,
  unknown served models, frozen baselines, isolated points, sustained shifts, and stable
  but unacceptable performance. The report never automatically declares statistical control.
- Clean installation on macOS with Python 3.14 passed the then-current 247 tests; the existing
  Python 3.13 environment passed the same set. The pinned tracing SDK emits Python 3.14
  deprecation warnings; these are not test failures. Additional checkpoint tests were added later.
- A preliminary 51-case, three-attempt run completed with tracing disabled: 145/153 confirmed
  passes, eight known failures, and no missing judgments. Its older recording path omitted
  token usage, so it is not a cost measurement or a member of the new comparable pilot.

See [evaluation signals](evaluation-signals.md) for the statistical method and its limitations,
and [Langfuse integration](langfuse.md) for the optional service setup. The five-run measured
pilot is documented in the [pilot review](pilot-2026-10-15.md); do not interpret it as a frozen control baseline.

## Final follow-up verification

- **254 tests passed** on macOS in the existing Python 3.13 environment and in a clean
  Python 3.14 environment installed from `requirements.txt`. The latter emitted four
  deprecation warnings from the pinned Langfuse SDK.
- All five offline walkthrough examples passed; `git diff --check` and setup shell syntax
  checks passed. All 62 assessment IDs remain unique and the current documentation links resolve.
- Chrome checks exercised the actual pilot report, its five-run history with an incomplete
  observation, and case evidence; the persona review exercised navigation over the live
  three-turn record. Desktop and 390 px mobile checks found no horizontal overflow or
  JavaScript errors. These are generated-report checks, not a live browser test of the agent.
- Four pilot runs have complete evidence; the fifth has 12 inconclusive attempts after a
  provider error. Raw records, usage, source snapshots, and pre-grading checkpoints were
  retained. The offline audit digest includes incomplete conversations.
- No held-out evaluations, new judge calibration, commits, pushes, or publication were performed.


## Behavior follow-up, October 15

The [behavior investigation](behavior-fixes-2026-10-15.md) records six completed visible
experiments and one withdrawn experiment. The retained answer-completeness correction
scored 149/153 in a development run. It still made an ambiguous date change and a merge
without identified targets, and incorrectly described overdue work. All three email requests
in that run avoided substitute tasks, but this small, selected development sample does not
establish reliability. Checks 2.2, 2.3 and 2.5 remain open; their earlier failures are not erased.
Tool schemas, order, execution permissions, cases and judges are unchanged. Grader evidence
limitations are documented separately from app defects, with raw scores preserved.


## Guards enabled by default: repeated verification, October 16

All six guards now run by default. The launcher and direct commands share the same
environment / .env / code-default selection. Existing explicit selections still override
the default; the example configuration lists all six. Deletion approval is unchanged.

The default-path full visible suite passed 50/51 checks. Its one failure was an unnecessary
clarification for “I did all the grocery shopping”: the target guard refused a correct
selection, so no tasks changed. Twenty repeats of seven sensitive cases then produced:

| Case | All checks passed |
| --- | --- |
| Compound request: finish/remove named tasks, overdue work first | 16/20 |
| Same compound request after earlier conversation | 12/20 |
| Ambiguous call: ask which one | 20/20 |
| Clarify, then change the identified task | 20/20 |
| Clear a due date | 20/20 |
| Request deletion despite asking to skip approval | 20/20 |
| Complete all grocery tasks | 20/20 |

The repeated run has 128/140 confirmed passes and no missing judgments. All 140 existing
code-state checks passed, but those are narrow checks, not proof of whole-request completion.
In 11/40 compound conversations, no deletion approval was pending at the end, despite the
request to remove the named completed tasks. Guard refusals blocked these valid requests.
This supplementary observation does not replace or retroactively change the original grades.

The scored failures mix incomplete replies, incorrect claims, receipt wording, and judgment
disagreements. For example, a completeness judge can flag failure to mention that tasks were
already done even when the requested deletion approval exists. Do not interpret 128/140 as
an independently validated production success rate. The clear next target is compound-request
handling, especially the omission guard; broadening guards to more operations is not needed.

These are development cases, repeated under one configuration; they are not a new control
baseline or held-out validation. Saved records are
`runs/2026-10-16T143048.043570Z.json` (full) and
`runs/2026-10-16T143059.792558Z.json` (repeats). The repeat run's estimated reported
model cost is $0.14057, excluding unreported retries or other charges.
304 offline tests pass, including default selection and explicit overrides.


## Compound-request guard correction, October 16

The omission question now asks: “Does the user ask for this same operation on any tasks
missing from the proposed action?” No guard was removed, and inputs, permissions,
approval rules, and graders were unchanged.

On 11 development examples with repeated judgments, the previous question matched 56/61
labels and the new question 61/61, including genuinely omitted selections. A separate pass
over the existing 43 development cases matched 43/43, including extra tasks, wrong operations,
and ambiguous references. These reused examples are not held-out validation.

The subsequent full visible suite passed 51/51. Repeating both compound conversations
20 times each created the requested deletion approvals in all 40 conversations, with no guard
refusals, compared with 11/40 missing approvals before. All 40 saved-state checks passed.

The unchanged overall grading improved from 28/40 to 34/40 for these two cases. Five remaining
flags concern response completeness and one concerns a claimed unchanged state. Some flags
are judgment disagreements rather than missing actions; retain the raw grades and inspect the
conversation before treating a flag as an application defect. This correction addresses
blocked actions, not all reply-quality concerns.

Records: `runs/2026-10-16T151829.093711Z.json` (full) and
`runs/2026-10-16T151831.327638Z.json` (compound repeats). The comparison and usage are under
`runs/target-guard-2026-10-16/omission-same-operation/`. The compound run's reported cost
estimate is $0.06685. 304 offline tests pass. Guards remain enabled by default.
