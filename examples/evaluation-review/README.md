# Open the example without running anything

[View the report online](https://eliasseninnovation.github.io/beyond-chat-todo/), or download this
repository and open `index.html` in a browser. It is a self-contained report from 20 real runs
of this repo's synthetic todo evaluations. No server, API key, internet connection, or
Langfuse instance is required. The page includes a chart, exact counts, and eight selected
conversations with application evidence for human review.

The chart's limits are **illustrative candidates**, not an accepted quality baseline.
Original results include both application mistakes and apparent grader mistakes. The
example teaches that complete measurement and a chart with no signals do not establish
acceptable behavior or good grading. It measures the historical configuration stated on
the page, not whatever code is currently checked out.

Use the dropdowns and notes to record your assessment, then **Download review notes** before
closing or refreshing. Notes are not autosaved and do not leave your browser until you
choose to save the downloaded file. Downloading does not change scores, train a grader,
update the repository, or approve a baseline. Do not put sensitive information in notes
you intend to share. The assistant's proposed interpretations are separate from your labels.

To regenerate the page after changing the renderer, from the repository root:

```bash
.venv/bin/python -m evaluations.eval_collection examples/evaluation-review/collection.json
```

This makes no model calls. `collection.json` contains all 20 run summaries and selected
conversations, with digests of their original source records. It is a curated review export,
not the complete raw collection or a source snapshot. The original local records are kept
under ignored `runs/`; `export.py` documents the exact selection and can recreate this
bundle when those original records are available. No paid run is needed to use this example.

Read [the evaluation workflow](../../docs/guides/evaluation-results.md) for everyday checks,
version changes and limits. Langfuse is an optional route to deeper traces; this example is entirely local.

To validate a downloaded review against the exact evidence bundle, without changing grades:

```bash
.venv/bin/python -m evaluations.eval_collection examples/evaluation-review/collection.json --notes /path/to/todo-evaluation-review.json
```

Validation checks the bundle identity and that each example has one recognized assessment.
It does not determine whether the person's judgment is correct or whether a grader is calibrated.


## What this example measures

The collection contains 20 runs of 51 cases, with three attempts per case: 3,060 attempts.
The original grades record 2,956 passes and 104 failures, with no missing judgments.
It used an earlier configuration with the merge guard enabled, before the additional
target/action guards now enabled in the sample. GPT-6 Luna served the agent and judges.
These results do not measure the current checkout.

No declared chart signal appeared in the collection, but review found both application
mistakes and apparent grading mistakes. That is the teaching point: consistent measurement
does not establish acceptable quality or a trustworthy grader. The eight selected
conversations let you inspect that distinction yourself. The chart limits remain
illustrative; this collection is not an accepted release baseline.
