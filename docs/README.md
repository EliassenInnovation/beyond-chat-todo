# Build Helpful, Trustworthy Agents Into Your Application

These documents help you decide what an agent should do in your application, connect it to
your existing capabilities, and evaluate whether it helps. The small todo implementation
makes the patterns concrete without requiring you to learn a complicated domain.

## A path from idea to implementation

1. **Understand the opportunity and the design choices.** Read the [design principles](principles/principles.md): shared capabilities, knowledge of the screen, caller-specific authority, and clear feedback.
2. **See the choices in code.** Follow the [walkthrough](guides/walkthrough.md), from one shared operation to approvals, failure recovery, and evaluation. No prior reading is required.
3. **Try it yourself.** Use the [setup instructions](../README.md#setup), then [configure your models](guides/models.md) for the agent, guards, and evaluation roles.
4. **Apply it to your app.** Use the [implementation guide](principles/implementation.md) to scope one capability and review it against concrete acceptance checks.
5. **Find out whether it helps.** Read [Evaluating agents](principles/evaluating-agents.md) for the method, then [reading evaluation results](guides/evaluation-results.md) for this sample's reports, human review, and control charts.

The principles, implementation guide, and evaluation method are the **Beyond Chat** document
series. Their check numbers support detailed reviews; you do not need to learn them to try
the sample or follow the walkthrough.

## Inspect evidence before running anything

[Open the evaluation report](https://bobfischer.github.io/beyond-chat-todo/) to inspect real
recorded results, a chart of repeated runs, and selected conversations. It needs no account,
model credentials, or running service. The [example instructions](../examples/evaluation-review/README.md)
explain offline access and review notes.

The [human-review example](guides/evaluation-results.md#from-exploration-to-human-judgment)
shows how to resolve questions about intent and proposed actions. Personas broaden exploratory
testing; review their flagged findings and sample apparent successes as well.

## Look up a specific question

| Question | Guide |
| --- | --- |
| Can I use a different model or provider? | [Bring your own model](guides/models.md) |
| How do I watch a persona or run it unattended? | [Persona instructions](../README.md#watch-personas-or-run-them-unattended) |
| When should I investigate eval variation or collect a new baseline? | [Read evaluation results](guides/evaluation-results.md) |
| How can I connect this sample to Langfuse? | [Optional Langfuse setup](guides/langfuse.md) |
| Which detailed checks does the sample meet, and what is missing? | [Sample assessment](guides/sample-assessment.md) |

Langfuse is an optional example integration. Local reports and human review work without it.
