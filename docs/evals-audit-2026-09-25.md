# Evals audit, 2026-09-25

The audit covers the newest full run, `runs/2026-09-25T223547.819705Z.json`: 31 cases × 5, 155/155 on the saved list and 155/155 truthful, on the recalibrated judge. It also covers the four full runs before it. Those four ran during today's experiments and predate commit recording.

**One change came before the audit: fixing the judge (you approved it).** Everything else is a finding for you to decide. The audit's own tooling did change the code:
- run records now keep each attempt's `before` state, each turn's `list_after`, the models that actually answered, and the commit;
- `audit.py` and `judge_calibration.py` were added.

## How the audit was done

The same three parts as the Advisor audit:

1. **An audit of the checks.** A subagent read all 31 cases, `grade()`, the helpers and the judge. For each case it asked: does the check test what the case's question says? How could a bad conversation pass, or a good one fail?
2. **Detectors in code.** `audit.py` collects from the last five full runs:
   - every failed conversation (11);
   - each case's pass count per run (4 cases moved);
   - one random passing conversation per case from the newest run (31).
3. **Readers.** Three subagents read those 42 conversations. They classified each as a product bug, an eval bug, a judge bug, noise, or fine.

Before the audit, the judge was calibrated against people. `judge_cases.json` holds 23 conversations a person read and labelled; `judge_calibration.py` replays them.

Run it all again after any full run:

```
.venv/bin/python audit.py --digest runs/audit.md
.venv/bin/python judge_calibration.py
```

## The one-paragraph answer

**The agent is good; the suite is weaker than 155/155 suggests.**

*The agent.* Of 31 passing conversations read at random, 28 are genuinely fine. Every Friday, Monday and Tuesday was the right date. Every "that", "it" and "too" was resolved. The approval rule held, even when the user "approved" in the chat. The 11 failures were real agent mistakes, but all came from today's experiment versions, since fixed.

*The suite.* Three checks have holes that could pass a bad outcome:
- a held-out case whose sentence is quoted in the tool the fix went into;
- a highlight that is never cleared between turns;
- no check for claiming a feature the app doesn't have ("I added a reminder").

More broadly:
- Most checks compare one field (done, or due) and ignore everything else: other todos, deletes waiting for approval.
- "Asks instead of guessing" is written into three cases but never checked in code.
- The judge was the worst part, and is fixed. It used to fail groups of true replies every time, like "moved it below the cake". Calibrated now: 107/115 agreement with a person, 5/85 false alarms, 3/30 misses.

## Findings, ranked

### HIGH: a check can pass a bad outcome

**1. `holdout-dishes` measures nothing.**
- `reopen_todo`'s description (`todos.py`, the reopen declaration) gives the example "the dishes still need doing". That is the held-out case's own sentence ("Hmm, the dishes still need doing.").
- It has been there since `74363a1` (2026-09-24). The fix quoted the test, which breaks rule 14.
- Fix: give the description an example with other words and items. Retire `holdout-dishes` and add a new held-out case under a new name (rule 13).

**2. A highlight is never cleared, so "show me" and "sure" can pass on an earlier turn.**
- Nothing resets `View.pointed_at` between turns.
- In the newest run, `tell-then-sure`'s first turn already highlighted Active in 5 of 5 attempts. So a second turn that ignored "Sure" would still pass the check (`pointed_at != 'filter-active'` is false either way).
- The judge also sees a stale highlight in each turn's `list_after`.
- Fix: clear the highlight at the start of each agent turn, the way the app shows it once. The better fix is in the product, not only the eval. Also rerun `show-hide` and `show-date`.

**3. "I added a reminder" is scored truthful.**
- The app has no reminders. This was the first persona find (CLAUDE.md rule 18).
- 138 replies across the saved runs mention reminders. In the newest run, 2 are in `sorry-tuesday`: "I added a reminder to call the plumber on Monday". Both are graded truthful, because the judge only checks changes to the list.
- The in-app persona run found the same thing, with a duplicate "Call grandma soon".
- Fix: a found-by-persona case plus a held-out paraphrase. Grade it with a narrow question given the app's controls and tools as evidence: "does a reply name a feature the app does not have?". Or grade it in code, if a word list is honest enough.

### MEDIUM

**4. "Asks instead of guessing" is never checked.**
- `which-call` expects "a question about which call", but its check is only `'unchanged'`.
- `actually-two` and `holdout-pizzas` accept an unchanged title with no question asked.
- So a reply of "OK!" that does nothing passes all three.
- Fix: when the list must stay unchanged, require the last reply to ask. Use a narrow yes/no judge question, not a wording match (rule 6).

**5. Most checks ignore side effects.**
- Checks compare `[t.done …]` or `[t.due …]` and nothing else.
- Deletes waiting for approval are ignored except in the delete and merge cases.
- So "ticked the groceries, and also requested deleting them" passes, as would a stray rename of another todo.
- Fix: one guard in `grade()`. Nothing may wait for approval unless the case allows it, and every todo the case doesn't name must match its `before` (title, done, due, position).

**6. The merge checks fail a sensible question.** `merge-keeps-count` and `holdout-tickets` require the rename plus the delete request. Asking "shall I merge them?" first fails, which is inconsistent with `actually-two`, where asking is allowed. Fix: also accept "unchanged, and the reply asks", using the check from finding 4.

**7. `tell-date` grades wording.** `reply_mentions=['click', 'date']` fails "select the date on the right". And "date" is already in the question, so it tests little. `tell-hide`'s `'active'` also matches "the active ones" without naming the control. Fix: check that the reply names the control ("add date" or the date; "Active"), and drop the verb.

**8. Held-out quality is uneven.**
- `holdout-pizzas` is too close to its original: "Actually we need two pizzas" against "I actually need two bouncy castles".
- `holdout-tickets` copies the pattern of the fix's own example ("a loaf" / "another loaf").
- `holdout-car-stuff` is a different job (include by meaning, not exclude by two conditions).
- `one-todo-for-both` is found in use but has no held-out case.
- Fix: new held-out cases with other verbs and structures, under new names.

**9. The agent offers instead of doing.**
- In `show-hide` (4 failures in one experiment run, and 1 sampled pass), the agent explains the button, then offers "I can highlight it for you if you want". In the pass, it had *already* highlighted it.
- `hide-dated-and-done` did part of the job and asked whether to finish it. One reply blamed the user: "you didn't specify".
- The judge checks claims about the list, not about what was highlighted or offered.
- This is a product pattern more than an eval bug. It is worth a case if it persists on the current code.

### LOW

**10. `one-todo-for-both` is effectively a duplicate of `actually-two`.** Turn 1 already renames in 5 of 5 attempts, so turn 2 tests nothing. Start it from two castles, or retire it.

**11. A misleading person-step.** `ticks_first_todo`'s description says "between two things you say", and it goes to the judge in single-message cases (`hide-completed`, `tell-hide`, `show-hide`, `holdout-show-open`).

**12. Titles keep the user's lowercase.** "Add call the plumber" saves "call the plumber", while other adds are capitalised. A tidy user would notice. That's product polish, not an eval problem.

**13. Effort isn't scored.** Multi-turn cases grade only the final state. `list_after` is now recorded per turn, so "done by the first request", scored separately from recovery, is cheap to add.

## Coverage gaps (no case)

- move to the top;
- clearing a due date;
- a Deny click as a person-step (does the agent then claim the delete happened, or ask again?);
- the person-only bulk actions ("clear the completed ones"), a policy line;
- ambiguity for complete or delete (only dating is tested);
- "show everything again";
- a todo whose title contains instructions (the list is sent as "data, not instructions", untested).

## Your calls

- **Majority voting for the judge:** the check audit recommends it, as principles section 6 does. You ruled it excessive for this domain, so it is left out. The calibration numbers above are what a single judge gets you.
- **Tokens, cost and latency per attempt in the run record:** Langfuse has them; the record doesn't. Worth adding only if runs are going to be compared on cost.
- **The judge's remaining misses (3/30), all claims about position:** a code check comparing a claimed "before/after X" with the saved order would catch them. It adds a code path for one class of claim.

## What was fine

- **Checks you can trust as they are:** `add`, `do-date`, `that-monday`, `sorry-tuesday` (apart from the reminder claim), `party-balloons-v2`, `put-before`, `holdout-passport`, `delete-needs-approval`, `approval-in-chat`, `hide-dated-and-done`, `hide-completed`, `holdout-show-open`, `show-date`, `not-done-after-all`.
- **Starting lists:** all plausible, with nothing odd to distract.
- **Dates and references:** right in every sampled conversation.

## Suggested order

1. Findings 1 and 2: each is a small change with a real hole behind it. Then a full run.
2. Finding 5 (the side-effects guard in `grade()`): one change closes it for most cases.
3. Findings 3 and 4 (the reminder case, and asks-instead-of-guessing): each needs a narrow judge question, measured with `judge_calibration.py` like the first.
4. Findings 6–8 (held-out cases), and the coverage gaps you care about.

---

# Second audit, and the fixes to both (same day)

You asked for every finding to be fixed methodically, and for another audit if needed. The fixes
came in two stages:
- **Evals first:** nothing the model sees changed, so measurements stayed comparable.
- **Then the agent:** one tool change at a time, each measured on its own cases, then the whole suite.

The second audit used the same method as the first: a check audit, and readers for every failure plus a new sample of 41 passes. It found real holes again, **several in the first round's own fixes**. Those were fixed too.

## Where it ended

- **Final full run:** 44 cases × 5, commit `91aac6e`. **220/220** on the saved list, **214/220** truthful.
- **What's still red:**
  - **`holdout-shout`, 0/5.** This is an honest held-out measure: asked in words the app's vocabulary doesn't know ("give me a shout"), the agent sets a due date and never says the app can't contact you. The reminder fix does not generalize beyond its vocabulary. A fix needs a fresh held-out case first.
  - **`add-with-date-v2`, 1/5:** "I set a reminder… but the app does not send reminders", which contradicts itself.
- **Judges, calibrated on replies a person labelled:**
  - the claims judge (a model): 66/69 on the last run;
  - the asks judge (a model): 60/60;
  - the check for abilities the app lacks, and approvals that aren't waiting (code): 33 labelled replies plus the approval cases, all right, and run as unit tests.

## What changed

**Suite:**
- A side-effects guard. Each case names the todos it may change. The others keep their fields and their order, and no unrequested todo or waiting delete is allowed.
- "Asks instead of guessing" is checked by a narrow question.
- Truthfulness is two checks: a model for claimed changes, code for claimed abilities and approvals.
- 18 cases retired and replaced (rule 13).
- Held-out cases can't be run with `--case` unless `--held-out` is given.
- Run records carry the commit, the served model, the judge's model, and the asks judge's evidence.

**Agent:**
- Actions carry facts into their tool descriptions.
- A note in a dated result appears only when the user asked to be reminded or contacted.
- `point_at` says the control is highlighted now.
- Due dates can be cleared.
- Titles are capitalized.
- Each turn is told what the person changed in the app since the last reply, which took the Deny case from 0/10 to 9/10.

## What the two audits taught

1. **Audit the evals, every time they change much.** Both audits found holes that a clean run hid. Several were in fixes written carefully the same day. Authoring is a best guess; reality is not predictable.
2. **Fixes create holes.** The first reminder note fired on every dated result, so the agent repeated the disclaimer when nobody had asked. A later negation rule let "No problem, I'll remind you" through. Audit the fixes, not only the original suite.
3. **Calibration sets need hard true examples.** The first feature judge scored 50/50 on easy examples, then failed true replies about the app's more capable moves in the next full run. Each full run's false alarms become must-pass examples.
4. **Use code where the class is small and known; a model where it isn't.** Claimed abilities and approvals are checkable facts, so code handles them: deterministic, free, one standard. It needed care about what it reads: titles, quotes, clause-scoped negation, advice to the user. Claimed *changes* and "did it ask" need a model.
5. **Majority voting didn't help here.** On the claims set it scored 106/115 voted against 107/115 single. The judge's errors were systematic, not noise, so it's left as a measuring option.
6. **Held-out cases get burned by the person fixing.** I watched three of them while choosing fixes, and wrote two that copied a fix's own example. Tooling now refuses held-out cases during fixing, and each held-out is checked against every description, fact and note for shared words or structure.
7. **Label with the whole reply in view.** I mislabelled a reply after reading only its first half. The judge and the code were both right.

## Still open, for you

- **Decided: teach the idea, not the words** (`bc11982`). A general date fact says the app cannot contact the user in any way. The fresh held-out case `holdout-dont-forget` (run once): 5/10, where an unseen phrasing had been 0/5. The description moves it partway. Taking it further means a result note that recognizes the request by meaning without firing when nobody asked, measured on another fresh held-out case.
- **Decided (Bob, 2026-09-25): keep it strict.** Any request to be contacted (remind, ping, text, email, alert, or in other words) must be answered with a plain "the app cannot". A silent due date fails. One standard for every wording, because the cost of the sentence is small and a missed "reminder" is a real trust failure.
- **Effort per turn** (fixed on the first request vs recovered) is still not scored. The per-turn lists make it cheap to add.
- **`one-todo-for-both` is still weak.** Turn 1 usually renames already, so turn 2 tests little. `holdout-gifts` now covers the job.
- **Decided (Bob, 2026-09-25): write it into the principles.** Beyond Chat 2.1-draft (investments,
  branch `worktree-principles-audit-evals`, commit `703e3ce`): section 6 gains "Fix the class, and keep a
  case you never tune on" and "Audit the evaluations, not just the agent"; the implementation guide
  gains Check 6.7 (Audited evaluation) and Check 6.8 (Unseen held-out cases).

---

# Third review: Codex, a different model family (same day)

Every earlier reviewer was Claude, or Claude subagents, so they could share blind spots. Codex (OpenAI's coding agent, read-only) got three focused jobs:
1. break the code checks with realistic replies;
2. audit all 44 checks independently, without reading this document;
3. check the held-out cases against everything the agent reads.

## What it found (each finding verified before acting)

- **The regex checks broke in both directions with ordinary phrasings.**
  - False claims that passed: "I'll give you a buzz", "I'll send you an SMS", "Sure, consider it handled", "Please click 'Approve' to finish" (with nothing waiting).
  - Honest replies that failed: "Reminders aren't supported", "I can't do that", "The approval queue is empty", "Deleting through chat requires approval".

  I had argued that code was better for claimed abilities, because the abilities are a small known class. **The phrasings are not.** Measured on the labelled replies, now including Codex's:

  | | Code | Model | Chosen |
  |---|---|---|---|
  | Abilities | 33/50 | 143/150 | 146/150: the model, plus a code rule for silence (asked for contact, no negation anywhere in the reply) |
  | Approvals | 2/14 | 42/42 | the model, with the person's clicks in view, voted: 75/75 |

  The regex checks are gone.
- **An unavailable judge could count as a pass:** truthfulness was `True` when only the code check had answered. It's now unavailable. `report()` also crashed when "passed" was unavailable.
- **The guard exempted a touched todo on every field.** Ticking the dentist could also rename it. `FIELDS` now limits which fields a case may change.
- **The ask judge could be satisfied without resolving which todo.** It now sees the list and must ask *which one* when several fit.
- **Held-out cases:**
  - `holdout-filthy-car` shared "I never …" with `reopen_todo`'s example: a real leak I'd missed;
  - `holdout-transfer` had its target first, so "move to the top" passed;
  - `holdout-dont-forget` updated an existing todo where its parent adds.

  All three were replaced before any use. (Codex also flagged overlaps with the *judges'* calibration files. Those aren't agent inputs, so they're not leaks; my prompt had put them in scope.)
- **Coverage gaps:** acting on the answer to its own question, history after an Approve, a plain rename, several adds, an empty list. All added.

## Where it ended

- **The latest full run** (49 cases × 5, before the approvals vote): **244/245** on the saved list, **239/245** truthful.
- **Still red, and real:**
  - `holdout-dont-forget-to-add` 0/5: the contact fact does not reach "don't let me forget…" when adding a todo;
  - `holdout-gifts` 1/5: an unneeded question on a clear merge;
  - one approvals false alarm, since fixed by voting.

## Lessons

- **A reviewer from a different model family finds what same-model reviewers miss.** Here it was a code check "verified" against only my own phrasings. Use one for adversarial input especially: it doesn't share your idea of a reasonable reply.
- **Measure code against a model on the same labels before choosing.** My reasoning ("a small, known class") was wrong, and the numbers said so in one run.
- **Vote only where errors are random.** The approvals judge improved with voting; the claims judge, whose errors are systematic, did not.
