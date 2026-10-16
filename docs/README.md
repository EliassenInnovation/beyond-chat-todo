# Documentation

Start with the walkthrough to see the principles in working code. The practical guides explain how to use and adapt the sample.

## Use and adapt the sample

| Guide | What it helps you do |
| --- | --- |
| [Walkthrough](guides/walkthrough.md) | Follow a request through the UI, shared actions, guards, approval, and undo. |
| [Bring your own model](guides/models.md) | Configure the agent, guards, judges, and persona model. |
| [Read evaluation results](guides/evaluation-results.md) | Interpret failures, missing evidence, repeated runs, and control charts. |
| [Optional Langfuse setup](guides/langfuse.md) | Connect this app to your own tracing project. |
| [Sample assessment](guides/sample-assessment.md) | See which implementation checks the sample demonstrates and what remains limited. |

For installation and commands, use the [repository README](../README.md).
For a report that needs no setup, open the [offline evaluation example](../examples/evaluation-review/index.html).

## Understand the principles

Read these in order, or use the checklist as a reminder once you know the approach.

1. [Design principles](principles/principles.md) — the reasoning behind the architecture.
2. [Implementation guide](principles/implementation.md) — a [quick checklist](principles/implementation.md#quick-checklist), followed by contracts and acceptance checks.
3. [Evaluating agents](principles/evaluating-agents.md) — the evaluation method beyond this sample.

## Try an evaluation review

The [offline example](../examples/evaluation-review/README.md) supplies real recorded
results and selected conversations. Use it to practice distinguishing application failures,
grader mistakes, and incomplete evidence without running models.
