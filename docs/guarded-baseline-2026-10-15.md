# Twenty runs with the merge guard enabled

The collection completed all 20 full visible-suite runs: 51 cases, three attempts per case,
3,060 attempts in total. Every attempt has its required judgments and outcome. The recorded
score is 2,956 passes and 104 failures (96.60% passes), with individual runs ranging from
143 to 151 passes out of 153. Estimated reported cost is $1.60413, plus a separately recorded,
small guard preflight call. These are usage estimates, not reconciled billing charges.

## What was measured

The collection used a frozen copy of the restored app with `todos.merge_unnamed` explicitly
enabled, including the visible-task-ID orientation change. GPT-6 Luna served the assistant,
judges and guard. Langfuse export was off, retries disabled, requests limited to 60 seconds,
and chat output capped at 4,096 tokens. The guard used the Decisions API and its own input-only
pricing. The first run ran alone; subsequent runs used up to four concurrent processes.
A shared conservative $5 allowance covered calls. No held-out cases were run.

The earlier, stopped guard-disabled collection is separate and excluded for a stated
configuration reason, not because of its scores. All 20 guarded runs are retained. Their
source snapshots, configuration fingerprints, usage, conversations and original grades remain
under `runs/guarded-baseline-2026-10-15/`. `index.html` links the individual reports;
`history.html` shows the latest run and comparable observations. The directory is locally
ignored by Git. A curated [offline review example](../examples/evaluation-review/index.html)
now includes all 20 summaries and eight selected conversations in the repository. It labels
candidate limits explicitly and preserves original grades; it is not the full raw collection.

## What the chart says—and does not say

Applying the existing individuals/moving-range calculation to all 20 observations gives:

| Quantity | Result |
| --- | --- |
| Average recorded failure rate | 3.40% |
| Lower calculated limit | −1.63% (outside the possible range) |
| Upper calculated limit | 8.43% |
| Declared signals found | None: no point beyond a limit, no eight consecutive points strictly on one side |

These are candidate limits calculated from the same observations being examined, not
independent confirmation of control. The negative lower limit illustrates the limitations of
this approximation for bounded, discrete rates. These back-to-back, partly concurrent runs
also do not represent variation across days or all operating conditions. There is no claim
of a particular false-alarm probability, release acceptance, or reliability on unseen requests.

**Do not yet freeze these as a baseline of application quality.** They describe the output of
this particular app-and-grader combination. Review found real application errors and apparent
measurement errors mixed into the score. A stable recorded score can include stable grader
mistakes. The collection is still useful evidence and a worked example of why measurement
quality precedes interpretation of a control chart.

## Review findings

The assistant reviewed the conversations for all 104 flagged attempts, their failed checks,
and relevant tool/state evidence. It also sampled one recorded passing conversation per run,
using the lowest SHA-256 of `review-v1:<run-folder>:<case>:<attempt>` among passing attempts.
This is an assistant review, not independent human labeling or a calibrated replacement score.
Original grades have not been changed.

| Finding | Evidence and interpretation |
| --- | --- |
| The narrow merge guard protected the ambiguous-merge case | All 60 `merge-which-two` attempts left tasks unchanged with no pending deletes. In 19 attempts the tool log records the guard refusing a proposed merge. Four attempts nevertheless failed the clarification judge despite replies asking which tasks. This is observed protection on one case, not a causal estimate against a contemporaneous unguarded control. |
| Ambiguous requests still produced unwanted changes elsewhere | `which-call-v2` failed 9/60 attempts after assigning a date without identifying which call; `clarify-then-do` failed 3/60 after changing both calls before clarification. The merge-specific guard does not cover these operations. |
| Unsupported work was sometimes replaced with an unwanted task | In 12/60 `no-email` attempts the assistant added an email task without being asked to add one. Six further attempts in this case were flagged as unanswered despite explaining that email was unavailable and supplying the list. |
| Compound requests can lose a component | Several overdue-task replies handled deletion but omitted or deferred the requested attention to overdue work. Other flags in the same cases concern replies that did show the overdue tasks, so their total failure counts cannot be equated with this one error. |
| Follow-up judgments need context | Ten `put-it-back` attempts were flagged as unanswered despite restoring the merge after undo. Both `put-before` flags show the requested task placed before the castles. The answer judge sees only the current user message and reply, limiting its ability to interpret these references. |
| Clarification and state checks can also misgrade | The four ambiguous-merge flags noted above involve a model clarification check included in the combined `passed` result. A failure named `passed` is therefore not necessarily a deterministic state failure. Two `one-todo-for-both` failures used “both” in place of an explicit numeric count, suggesting the title/count check also needs review. |
| Approval guidance remains a concern | Some replies told the user to click an approval card after the request had been denied and the card was gone. Other flagged replies gave a sequence of controls that needs checking against the actual human UI path. Do not dismiss all eight approval flags as grader noise. |
| At least one positional error is clear | `back-there`, run 19 attempt 2, returned the dentist task to second rather than its original third position. |

The small passing sample included correct additions, date edits, clarification, view changes,
merge/undo, approval follow-up, and a reminder limitation. It is not a false-negative-rate
estimate and does not establish that the remaining passing conversations contain no errors.

## Next use of the evidence

Preserve this collection unchanged. Prioritize grading review: give contextual judgments the
evidence needed to interpret the conversation, obtain independently reviewed labels for the
clear false-alarm candidates, and test any revised grader on both correct and incorrect replies.
Do not silently turn these flags into passes or quote an adjusted success rate from this review.

Separate application fixes from grading fixes. Use focused repetitions and a full regression
run as described in [Reading evaluation results](evaluation-signals.md), rather than ordering
another 20-run collection for every change. A new grading method starts a distinct measurement
period; it cannot inherit these limits without review. If saved conversations are regraded,
retain both versions and label the new results as rejudged, not new application runs.
