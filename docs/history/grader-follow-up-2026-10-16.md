# Grader follow-up, October 16

This work reuses saved synthetic conversations. It does not run the application again,
change its actions, or replace the original 20-run collection. Original grades remain
available. A change in measurement must not masquerade as an improvement in the app.

## Clarification: keep the existing grader

A narrow candidate added one rule: a question can resolve the user's meaning without
naming a proposed list operation. The comparison used the same 20 existing labeled
examples and two assistant-reviewed examples as the prior comparison, three judgments
per example per version. Both versions agreed with 65 of 66 labels; all judgments were
readable. Estimated reported cost was $0.00991.

The old version rejected one genuine clarification about which call the user had made.
The candidate avoided that disagreement but accepted a reply that told the person to
check whether tasks were needed without asking them a question. This does not establish
an improvement. The candidate was not adopted.

These are reused development labels, with mixed review provenance, not independent human
validation. Repetition measures judge variation on these examples; it does not enlarge
the set of distinct examples. Frozen prompts, evidence, labels, usage and results are in
`runs/clarification-review-2026-10-16/` locally.

## Report: distinguish complete evidence from comparability

The report previously called evidence incomplete when comparison metadata was absent or
when a record had been rejudged. Evidence completeness now depends on the attempts,
outcomes and required judgments. Comparison eligibility remains a separate condition.
A rejudged report prominently says the application was not rerun and that it is excluded
from control-chart comparisons. It shows the additional judge cost separately from the
original run cost. Missing judgments still make evidence incomplete.

## Claim checking: test each reply against its own time

A second candidate checked each reply separately, with its preceding conversation and
current state but no future turns. The existing question stayed the same, with an
instruction to grade only the final reply in that call. This isolates a possible source
of false alarms: a statement can be true before the person changes the list.

On 49 existing claim-label fixtures and four assistant-reviewed examples, each repeated
three times, the original matched 153/159 labels and the candidate 155/159. All judgments
were readable. The candidate needed 255 model calls versus 159, and the comparison cost
an estimated $0.03545 in total. Both accepted the two correct initial task counts in all
six judgments, so this comparison did not reproduce their original false alarms. Both
also missed the same wrong-position claim in all three repetitions. The candidate
introduced one disagreement on another previously accepted example.

This small net gain on reused development examples does not justify adopting the more
expensive path yet. The existing claim grader remains in place. The unresolved issue is
both missed false claims and occasional rejection of true statements, not just a missing
prompt instruction. Sources and results are preserved locally under
`runs/claims-turn-review-2026-10-16/`. Existing judge fixtures were used as supplied; the
new initial-count examples went through the application's receipt-removal transformation.
This is not a validation of every production grading path.

## Completeness: all 20 saved runs rejudged

The retained contextual completeness grader rejudged all 3,060 attempts in the original
20-run collection. All returned usable judgments: 4,317 judge calls, estimated reported
cost $0.43593. The conservative budget ledger charged $0.57851 of its $1.50 allowance.
There were no application calls, no Langfuse export and no missing judgments.

| Completeness transition | Attempts |
| --- | ---: |
| Pass remained pass | 3,001 |
| Fail remained fail | 22 |
| Fail became pass | 28 |
| Pass became fail | 9 |

With every other check unchanged, overall passes moved from 2,956 to 2,974 out of 3,060
(104 versus 86 failures). This is a measurement comparison, not an application improvement.
Original record digests, conversations, saved states and all other check results were
verified unchanged. The separate records and review page are in
`runs/answers-regrade-2026-10-16/`; open `index.html` to inspect disagreements, with newly
flagged failures first. The portable public example still shows the original collection.
No control baseline has been accepted or refitted.

The assistant reviewed all 37 changed judgments. Ten correct “put it back” responses,
two correct positioning responses and six honest email limitations now pass completeness.
Several compound overdue-task requests also benefit from the prior state: the two tasks
were already complete, so the response need not announce completing them again.

The new results also expose remaining problems:

- `tell-hide-v2`, run 20 attempt 2: a correct explanation to click **Active** is newly
  rejected. This is a clear completeness false alarm.
- `clarify-then-do`, run 17 attempt 2: the quoted missing question is the assistant's earlier
  “Which Monday’s date should I use?”, not the current user's request. Context must not
  cause the judge to grade the wrong speaker's obligations.
- Other `clarify-then-do` and `which-call-v2` flags concern guessing which call. That is a
  real behavior concern, but completeness should remain separate from correctness. The
  multi-turn case's final-state check does not establish that clarification preceded the
  change. That sequence deserves a separate, explicit check rather than relying on the
  completeness judge to catch it incidentally.
- `overdue-first`, run 2 attempt 3, now passes with “I'll leave the overdue tasks alone for
  now.” It acknowledges that part without helping the person start it. Whether the reply
  addresses a request and whether it does the requested job are different questions; the
  application outcome check needs to express the latter clearly.
- Adding new tasks to check whether existing tasks are needed remains an unwanted-action
  issue. Regrading completeness does not resolve it; other failures were preserved.

These findings support retaining conversation context, but not declaring the grader
reliable enough to replace review. No new labels were silently applied to the original
collection. The next work should make the outcome and sequence checks explicit, and test
speaker/turn boundaries in the judge, rather than add case-specific phrasing rules.

Verification: 277 offline tests passed. The regraded report's notice, evidence status,
desktop/mobile layout, absence of horizontal overflow and lack of external requests were
checked in isolated Chrome. All paid comparisons are complete. Nothing was committed or
published.

## Clarification sequence check implemented

`clarify-then-do` is now retired in favor of `clarify-then-do-v2`. The first user turn
must leave the list and view unchanged (a highlight is allowed), and its reply must ask
for clarification. After the user's answer, the final list must have the requested date
on the correct task. These conditions belong to the outcome check, separate from the
completeness judge. No application prompt, capability or guard changed.

The case declares `clarify_on=1`. Code compares that turn's saved state with the state
immediately before it. An observed change fails without a model call. Otherwise the
existing clarification judge assesses that turn's reply, not the final reply. Missing
state or an unavailable judge cannot pass; a known failure still takes precedence over
missing evidence. The record retains the clarification verdict and reason, and the report
shows an early-change failure rather than blaming only the final saved list.

An offline replay of the state check over the 60 original `clarify-then-do` attempts found:

| First-turn state | Final state | Attempts |
| --- | --- | ---: |
| Unchanged | Correct | 43 |
| Changed before clarification | Correct | 14 |
| Changed before clarification | Incorrect | 3 |

The 14 middle-row attempts demonstrate the gap in final-state grading. This replay did
not rejudge whether the unchanged replies ask, and is not a full revised pass rate.
Results are saved separately in `runs/clarification-sequence-2026-10-16/state-check.json`;
original records remain untouched. No model calls were needed.

The checkpoint observes state at the end of a turn. It does not detect a temporary change
undone within that same turn. Detecting every intermediate mutation would require richer
execution evidence. The existing clarification judge also retains its documented limitations.
Unit tests cover early changes despite correct final state, missing evidence, unavailable
judgments, harmless highlights, pending deletions, and selecting the intended turn.


## Receipt context: keep the delivered reply available

Removing code-written receipts before grading also removed the task names needed to
understand “Both are already marked done.” The claims judge now receives the full delivered
reply alongside the model claims it must assess. Receipts provide context and remain checked
separately by code.

A first layout, putting the full reply in a separate context field, did not improve agreement
and was rejected. Making the delivered reply the primary conversation text matched all
18 judgments on six assistant-labeled examples, three repeats each. The same prompt without
receipt context matched 11/18. Incorrect completion, premature deletion, and incorrect named
references were included; these are development examples, not independent validation.
The saved application runs are regraded separately. Their original scores and source
snapshots remain intact; the regraded copies are excluded from control-chart comparisons.

With only claims regraded, the targeted record changed from 11/12 to 12/12 and the
full visible record from 49/51 to 50/51. The remaining failure is genuine: the optional
omission guard blocked a valid deletion request and the assistant skipped the overdue
part of the request. Passing saved-state checks alone did not establish task completion.
