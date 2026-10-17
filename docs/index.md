<h1 id="cover" class="cover-anchor" aria-label="Cover"></h1>

![Build better agents. Help your users get things done. Eliassen Group.](images/guide-cover.svg){ .publication-cover }

<h1 id="introduction">Introduction</h1>

An AI agent embedded in an application can help people find useful capabilities,
understand unfamiliar workflows, and get work done.

For that agent to be useful, it needs a connection to the application. Depending on the
job, it may need to see what you are doing, control the interface, and perform tasks on
your behalf. It must also be safe and trustworthy. High-impact actions should require
your approval through a process enforced by application code. The application needs
controls and evaluation to keep the agent's advice and actions within applicable policies.
Where required, it should keep an audit trail of the interaction, approvals and actions taken.

Building this kind of agent can be challenging: designing tools, tuning prompts, and writing
application code to guide its behavior. Supporting agents can help with specific judgments
or checks where they are useful. There is no exact formula. It requires deliberate
experimentation, measurement and ongoing evaluation as models and applications change.

If this sounds like a lot of work, it is. But that effort should be weighed against the
friction your users already face: struggling to complete tasks, finding help that does
not help, being unable to reach a person when they need one, and encountering dead ends.

If your users experience these frustrations—or never discover capabilities that could
make their work easier—building an embedded agent may be worth the investment.

This guide explains how to approach that work. It is for developers, architects, and
product people adding an agent to an application or website—or improving one they already
have. A small TodoMVC-style application makes the design choices concrete without
requiring you to learn a complicated business domain. Managing todos is the teaching
example, not the reason to build an agent.

The chapters that follow explain why an embedded AI agent can be valuable and how to
design and evaluate one, using an agent in a simple todo application to illustrate the
principles and practices.

> **Security scope:** These practices address agent behavior and do not make an application secure. Authentication, authorization, encryption, transport security, and other application security controls require separate design and review under your organization’s security policies.

## Choose a way through the guide

You do not need prior experience with agents or jobs to be done. The design chapters assume
familiarity with an application's screens and workflows. The implementation chapters add
Python and API details; you can read the examples without running them.

<div class="reading-paths" markdown="1">

| If you want to… | These chapters explain… |
| --- | --- |
| Decide where an agent could help | [Why an embedded agent?](guide/why.md) — Consider where users struggle in your applications today and how an agent could help them get things done. |
| See how to build one | [Run the sample](guide/start.md) and [Follow a request](guides/walkthrough.md) — See how the UI and agent use the same application capabilities, with different permissions. |
| Evaluate and iteratively tune an agent | [Evaluate outcomes](guide/evaluation.md) and [Review results and understand variation](guides/evaluation-results.md) — Evaluate how well it helps users, review failures, and distinguish normal variation from changes that need investigation. Use what you learn to improve the agent and evaluate it again. |
| Apply this to your application | [Apply it to your app](guide/apply.md) — Choose a first capability, define its safeguards, and decide how to test it. |

</div>

We’ve added **Consider** and **Practice** boxes throughout the document to help you deepen
your understanding and apply the ideas to your own application.

## See the ideas in a working application

The guide includes a small todo application with an embedded AI agent. You can use its
controls yourself or ask the agent to help. Both use the same application capabilities
and data, with permissions appropriate to each.

![The sample application and its embedded assistant, with a human exploratory tester.](images/exploratory-tester.png)

*Trying the agent while watching what changes in the application.*

You can explore the code, [run a walkthrough without an API key](guide/start.md), or
[review recorded evaluation results](https://bobfischer.github.io/beyond-chat-todo/)
without installing the app. The sample is designed for local, single-user use and makes
the principles concrete.

The sample has been tested with OpenAI and Anthropic models. You can also connect hosted
or local models through an OpenAI-compatible API. The [Choose models](guides/models.md)
chapter explains the required features and how to check compatibility.

You can also explore detailed traces with Langfuse, which records model requests, tool
calls and results to help you understand what happened. Langfuse can run locally in
containers, without a cloud subscription. It is one example of a tracing tool; the sample
and its evaluation reports work without it. [Optional tracing](guides/langfuse.md)
explains how to connect it to the todo app.

## Apply the principles to your own application

The [implementation and acceptance checks](principles/implementation.md) help you plan
changes and review what you build. The [sample assessment](guides/sample-assessment.md)
shows which principles the todo app demonstrates and where you will need to do more for
your own application. [Sources and further reading](reference/sources.md) provide
additional background.

The guide and sample are provided by Eliassen Innovations under the repository's MIT license.
