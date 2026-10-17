# Build helpful, trustworthy agents into your application

An agent can help people use capabilities they cannot find, understand unfamiliar workflows,
and carry out work with them. Making that assistance useful takes more than a chat box:
the agent needs a connection to the real application, appropriate authority, and evidence
that it understands and helps.

This guide explains how to build that connection. It is for developers, architects, and
product people adding an agent to an application or website—or improving one they already have.
A small TodoMVC-style application makes the design concrete without requiring you to learn
a complicated business domain. Managing todos is the teaching example, not the reason to build an agent.

## The path through the guide

Start with [why an embedded agent helps](guide/why.md) and [how the pieces fit](guide/design.md).
Then [run the sample](guide/start.md) and [follow a request through its implementation](guides/walkthrough.md).
The walkthrough is the center of the guide: each design choice has a problem, a mechanism,
and a place to inspect it in code.

Continue with [model choices](guides/models.md), [exploratory testing](guide/exploration.md),
and [evaluation](principles/evaluating-agents.md). Learn to read
[evidence and variation](guides/evaluation-results.md) before treating a pass rate as a verdict.
[Tracing](guides/langfuse.md) is optional; local reports work without a running service.
Finish by [applying the approach to your own app](guide/apply.md).

## What you can inspect now

![The sample application and its embedded assistant, with a human exploratory tester.](images/exploratory-tester.png)

*The UI and assistant work on the same application state. This is one interaction, not a reliability claim.*

You can read the code, run the capability walkthrough without credentials, or
[open recorded evaluation results](https://bobfischer.github.io/beyond-chat-todo/) without installing anything.
The sample is local and single-user. It demonstrates patterns; it is not a complete production architecture.

## How the reference material fits

The accompanying design documents are called **Beyond Chat**. The
[principles](principles/principles.md) explain the broader rationale. The
[acceptance checks](principles/implementation.md) turn that rationale into things to inspect,
and the [sample assessment](guides/sample-assessment.md) records coverage and limitations.
Their numbered checks are reference identifiers, not concepts you need to memorize before starting.

The guide and sample are provided by Eliassen Innovations under the repository's MIT license.
