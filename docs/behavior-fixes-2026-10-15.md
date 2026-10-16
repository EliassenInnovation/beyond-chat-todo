# Behavior fixes — October 15, 2026

This follow-up investigates the clarification and unwanted-task failures from the [initial pilot](pilot-2026-10-15.md). The retained change corrects a conflicting instruction: the agent must answer every part of a request while grounding change claims in tool results. The previous instruction to say only what changed could exclude questions and actions the app cannot perform. Execution permissions, domain operations, tool schemas, tool order, cases, and judges are unchanged. This is model guidance, not a new execution-time guarantee.

## Measurements

Every completed experiment used 51 visible cases with three attempts each. The four complete baseline runs scored 145, 142, 144, and 145 out of 153. The incomplete baseline run remains retained and is not silently counted as a full observation.

| Candidate | Confirmed passes | Known failures | Inconclusive | Estimated reported cost |
| --- | ---: | ---: | ---: | ---: |
| Target-selection guidance alone | 144/153 | 9 | 0 | $0.0999 |
| Addition-tool contract alone (not retained) | 146/153 | 7 | 0 | $0.0991 |
| Answer-completeness guidance alone | 149/153 | 4 | 0 | $0.0932 |
| Combined guidance, run 1 | 142/153 | 11 | 0 | $0.0799 |
| Combined guidance, run 2 | 146/153 | 7 | 0 | $0.0911 |
| Combined guidance plus computed overdue facts (not retained) | 146/153 | 7 | 0 | $0.0942 |

These are small development samples, not a held-out result, a statistical-control claim, or a formal estimate of improvement on arbitrary requests. The runs overlapped in time; provider conditions and caching were not independently controlled. The combined checks are a new configuration and do not extend the original pilot’s comparison period.

## What was changed and why

- **Target-selection experiment, not retained:** extra guidance explained that names, references and group criteria identify targets, while resemblance alone does not. The two combined runs scored 142/153 and 146/153, and still made incorrect changes during clarification. The experiment did not establish a consistent benefit.
- **Answers:** the old priority said to reply with only what changed. The revision asks for a response to every part of the request, including work not done or unavailable, while requiring tool evidence for change claims.
- **Rejected addition rewrite:** a broader description of when to add tasks still created unwanted email tasks in two of three attempts. It did not establish the intended benefit, so it is not retained. An earlier version was stopped during contract review because its wording could conflict with the established dated-task/reminder behavior; its partial records and $0.0225 conservative ledger are retained.

The answer-only candidate scored 149/153. All three email requests correctly explained the limitation without creating substitute tasks; all three still-needed questions asked before changing the list. Three real errors remained: one ambiguous date change, one merge without identified targets, and one incorrect statement about which tasks were overdue. A fourth failure appears to be a grading problem, described below. Selecting this candidate after inspecting development results introduces selection bias; the score is not a verified reliability estimate.

- **Computed-facts experiment, not retained:** the read returned the observation date, overdue task IDs and count from domain code. Three deterministic tests checked date boundaries, read-only behavior and detached results. The model still omitted overdue work despite receiving correct facts. The experiment combined these facts with the extra target guidance; it does not isolate their effect, and does not measure combining them with the retained answer-only change.

No test sentences or item names were inserted into the agent guidance. No new keyword filter, permission exception, or stronger model was introduced.

## Grading concerns retained for review

The coding assistant inspected the failures. These are review findings, not independent human labels; raw verdicts remain unchanged.

- Addition-only, `one-todo-for-both` attempt 3: the final single task said “Get both bouncy castles at the same time.” The code grader recognizes only “two” or “2.” That is a wording limitation in a purported outcome check.
- Target-only, `hide-completed` attempt 3: the reply said the completed task was hidden, and the saved view did hide it, but the claim judge rejected that statement.
- Addition-only, `back-there` attempt 1: the agent asked whether to restore the previous position, an explicitly permitted response for this case, but the question judge classified it as not asking.
- Answer-only, `one-todo-for-both` attempt 1: the final state was one correctly renamed task; the answer judge said the request for one task went unanswered.
- Combined guidance: some follow-up replies about moving or restoring a task were rejected even though the saved outcome matched the request. The answer judge lacked prior conversation and state evidence; these need review, not an automatic pass override.
- The earlier concern about failing to acknowledge already-completed tasks remains unresolved with the owner. It is not silently accepted as either a defect or a corrected grade.

The answer judge receives only the current message and reply, not prior turns or saved state. That limits its evidence for follow-ups. Improving its evidence and calibrating it against independently reviewed examples is separate work; it was not changed during this comparison. The incorrect statement that only one of two tasks was overdue in the answer-only experiment was a real application error and was correctly flagged.

## Evidence and safeguards

Agent and judge requested and reported GPT-6 Luna. Langfuse export was disabled. Requests used a 4,096-token output cap, 64 KB serialized-request limit, 60-second timeout and no automatic SDK retries. Each full experiment had a conservative $0.45 allowance; unknown usage would stop further calls. These bounds belong to the recorded experiment wrapper, not the default app. Source snapshots and the wrapper’s hash preserve what was measured.

Raw JSON, usage and scenario checkpoints are retained locally under `runs/behavior-2026-10-15/`. Generated records are gitignored; fresh clones run their own experiments. No held-out case was selected or run. No source changes were committed, pushed or published.

| Candidate | Local record | SHA-256 |
| --- | --- | --- |
| Target-selection guidance alone | `target-contract/2026-10-15T153746.590689Z.json` | `d5804b6c19f0738c3b891c495931144a268f9a2582a96dae9cf827b600d72f0b` |
| Addition-tool contract alone (not retained) | `add-contract-v2/2026-10-15T154102.141318Z.json` | `f03a075755e905f49f2f9f6d119211fa12eecc5af22fd6210bc6d2f09ea36340` |
| Answer-completeness guidance alone | `answer-contract/2026-10-15T154245.943190Z.json` | `cf621be25d37de7baf14adb48d0afc0167191df0065aaca41c948971dbd2ffd5` |
| Combined guidance, run 1 | `combined-1/2026-10-15T160930.271502Z.json` | `36a3606a664ee57d595779ae23896916af3611ba34ebf59f307da4dad8c2bf5c` |
| Combined guidance, run 2 | `combined-2/2026-10-15T160930.271296Z.json` | `59db8b055ec385f8c27df6c24b38cb9adfdc6babf3fc700f011501aee9e8b7ae` |
| Combined guidance plus computed overdue facts (not retained) | `computed-overdue/2026-10-15T162700.871742Z.json` | `e08392e8e4776dd46b04fda271b5fdf90043caa80c028eef531827a605850ed3` |

## Follow-up work

Resolve the remaining ambiguous-target and multi-part-request failures before treating this as reliable unattended task management. Review the answer judge with conversation and state evidence and independent labels before changing grading policy. Keep the original verdicts and distinguish any regrading from new model measurements. The computed-facts experiment remains available for a future isolated test; its correct calculation did not establish correct conversation behavior.

Three additional explicit-task probes passed against the combined-guidance candidate: requests to create tasks about email or texting still created the requested task without claiming to send anything. These are development probes, not measurements of the retained answer-only candidate or held-out evidence.

## Proposed next evaluation: each part of the request

The owner suggested breaking a request into component parts and judging each separately.
For fixed cases, declare the expected parts before viewing the answer. For example:

| Requested part | Evidence to examine |
| --- | --- |
| Mark the named tasks done | Resulting task state; already-done tasks need no new change |
| Remove those tasks | Correct deletion proposals and an accurate explanation of approval |
| Start with overdue work | Correct identification of overdue tasks and a useful next step |

Do not invent an extra requirement to say “already done” merely because those words are
missing. Whether the requested order of work matters should also be explicit in the case.
Use code to verify state and approval boundaries; use a calibrated judge for conversational
requirements. Supply prior conversation, relevant tool results and saved state. Record a
verdict and cited evidence for each part, including insufficient evidence, and retain an
independent check for unwanted changes. Completing every requested part does not excuse
an unrelated extra action.

The HTML report could show these parts as rows with the expected outcome, observed evidence
and verdict. This is a proposed grading revision, not implemented or applied to these scores.

## Cost and verification

The six completed full experiments have $0.5573 in reported-usage cost estimates. Including the withdrawn experiment and three extra probes, the conservative ledger for this follow-up is $1.3704. The earlier measured work adds $1.7449 to that conservative ledger. An original uninstrumented run remains unpriced; a further $1 planning reserve was kept for it. These are estimates, not a reconciled provider invoice. No more paid runs are active.

After applying the retained correction, all 254 offline tests passed. Runtime, domain, policy, case and judge source hashes match the measured configuration. Tool schemas and order retain their previous hash. Updated documentation links resolve; the local HTML report was regenerated for the 149/153 record. `git diff --check` passed.

