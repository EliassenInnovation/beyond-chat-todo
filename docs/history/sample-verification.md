# Sample verification history

These measurements span several development configurations. Read the [current sample assessment](../guides/sample-assessment.md) for scope and limitations.

## Verification for this revision

- macOS, the repository's existing Python 3.13 environment: **225 tests passed** (`python -m pytest -q`). This includes Streamlit AppTest, the existing talk-anchor tests, and 32 added regression cases.
- `python3 -m todo.walkthrough`: all five offline examples completed and their assertions passed.
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

See [evaluation signals](../guides/evaluation-results.md) for the statistical method and its limitations,
and [Langfuse integration](../guides/langfuse.md) for the optional service setup. The five-run measured
pilot is documented in the [pilot review](../history/pilot-2026-10-15.md); do not interpret it as a frozen control baseline.

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

The [behavior investigation](../history/behavior-fixes-2026-10-15.md) records six completed visible
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
