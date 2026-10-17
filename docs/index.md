<h1 id="cover" class="cover-anchor" aria-label="Cover"></h1>

![Build better agents. Help your users get things done. Eliassen Group.](images/guide-cover.svg){ .publication-cover }

An AI agent embedded in an application can help people find useful capabilities,
understand unfamiliar workflows, and get work done.

For that agent to be useful, it needs a connection to the application. Depending on the
job, it may need to see what you are doing, control the interface, and perform tasks on
your behalf. It must also be safe and trustworthy. High-impact actions should require
your approval through a process enforced by application code. The application needs
controls and evaluation to keep the agent's advice and actions within applicable policies.
Where required, it should keep an audit trail of the interaction, approvals and actions taken.

Building this kind of agent takes work: designing tools, tuning prompts, and writing
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

Follow the chapters from motivation and design through the working sample and evaluation,
or use the chapter navigation to go directly to what you need.

> **Security scope:** These practices address agent behavior and do not make an application secure. Authentication, authorization, encryption, transport security, and other application security controls require separate design and review under your organization’s security policies.

## Choose a way through the guide

You do not need prior experience with agents or jobs to be done. The design chapters assume
familiarity with an application's screens and workflows. The implementation chapters add
Python and API details; you can read the examples without running them.

| What you want to do | Start here | What you can take away |
| --- | --- | --- |
| Decide where an agent would help | [Why an embedded agent?](guide/why.md) | One user job worth improving. |
| See the approach working | [Run the sample](guide/start.md), then [follow a request](guides/walkthrough.md) | A working example of shared operations and caller-specific authority. |
| Assess an agent you already have | [Evaluate outcomes](guide/evaluation.md), then [read the report](guides/evaluation-results.md) | Evidence to distinguish application failures, grading problems and ordinary variation. |
| Plan a change to your own app | [Apply the approach](guide/apply.md) | A scoped first capability and the evidence needed to review it. |

The **Consider** and **Practice** boxes are optional. Use one application and one user job
throughout; each prompt adds to a small design note you can use with your team.

## What you can inspect now

![The sample application and its embedded assistant, with a human exploratory tester.](images/exploratory-tester.png)

*The UI and assistant work on the same application state. This is one interaction, not a reliability claim.*

You can read the code, run the capability walkthrough without credentials, or
[open recorded evaluation results](https://bobfischer.github.io/beyond-chat-todo/) without installing anything.
The sample is local and single-user. It demonstrates patterns; it is not a complete production architecture.

## Read the guide and use the review references

The design chapters explain shared capabilities, user requests, authority, tools and interfaces. The implementation chapters take those ideas through the working app. The evaluation chapters cover exploration, judging, evidence and variation. These are parts of one guide, from the reason to build an agent through the evidence needed to improve it.

Use the [implementation and acceptance checks](principles/implementation.md) when scoping or reviewing work. The [sample assessment](guides/sample-assessment.md) records what this app demonstrates and what it leaves out. Check numbers are stable review identifiers; you do not need to memorize them before starting. [Sources and further reading](reference/sources.md) support the guidance.

The guide and sample are provided by Eliassen Innovations under the repository's MIT license.
