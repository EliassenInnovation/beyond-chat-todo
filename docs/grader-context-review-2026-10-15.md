# Completeness grading with conversation context

The retained change gives the completeness judge earlier conversation turns and the state
before and after the current turn. Its question explicitly accepts equivalent wording and
honest limitations. It judges whether a request was addressed, separately from whether the
action was completed or the response was true. The user confirmed these principles during
review: an inability to email can address an email request; a correctly restored change can
address “put it back” without repeating that phrase.

Only earlier turns are supplied as history. Human actions between messages are included.
Expected answers, grades and future messages are excluded. Existing labeled examples without
context still work. The application, merge guard, cases and their expectations are unchanged.

## Measured comparison

We compared the previous graders with candidate completeness, clarification and claim-checking
graders using GPT-6 Luna. Each arm judged each example three times: 129 existing labeled
examples plus eight assistant-reviewed development examples from the guarded collection,
822 judgments overall. All returned readable judgments. Estimated reported cost was $0.07546;
the conservative ledger remained within its $0.50 allowance. There were no new app runs,
no held-out app cases, and no Langfuse export.

| Label set | Previous grader agreement | Candidate agreement | Decision |
| --- | --- | --- | --- |
| Existing completeness: 60 examples × 3 | 177/180 | 178/180 | Retain the context change, with limited evidence of benefit |
| Reviewed completeness: 4 examples × 3 | 9/12 | 12/12 | Supports resolving follow-ups and limitations in context |
| Existing clarification: 20 examples × 3 | 58/60 | 55/60 | Revert candidate changes |
| Reviewed clarification: 2 examples × 3 | 6/6 | 6/6 | No demonstrated gain |
| Existing claims: 49 examples × 3 | 146/147 | 142/147 | Revert candidate changes |
| Reviewed claims: 2 examples × 3 | 3/6 | 3/6 | No demonstrated gain |

These are agreements with labels, not established human-judgment accuracy. Existing repository
labels have mixed review provenance. The eight new labels were assigned by the assistant;
the user confirmed the general completeness principles, not each individual label. Repeated
judgments are not independent new examples, and the small differences do not establish
statistical significance. This was a development comparison, not an unseen final validation.

The existing labeled sets contain both acceptable and incorrect replies. The added examples
include an omitted overdue-work request, an ambiguous change made without clarification, and
a task returned to the wrong position, as well as apparent false alarms. The judges never
received the expected labels. All arms, results and candidate prompts are preserved under
`runs/judge-context-2026-10-15/`; that ignored local directory is not yet a public artifact.
The claim comparison exercised the judge functions with supplied evidence, not a full replay
of every production grading transformation. Neither the candidate claim prompt nor its proposed
full-reply/date evidence path was retained.

## What remains unresolved

Clarification and claim judgments still need work; this comparison did not justify replacing
them. The title/count check that rejects “both” also remains unchanged: simply accepting the
word anywhere would create a different error, and a corrected expectation should receive a
new case identity under the repo's retirement rule. The receipt-repetition constraint remains
pending direct rendering of application receipts. These concerns are not declared solved.

No original grade was changed, no corrected pass rate was invented for the 20-run collection,
and no baseline was frozen. Future results with the contextual completeness grader constitute
a different measurement configuration. A later regrading of saved conversations must be saved
separately and labeled as rejudged.

Offline tests verify evidence boundaries and preserve pass/fail/unavailable handling. Independent
human review of the development labels and further representative examples would strengthen the
basis for using this judge in a release decision.
