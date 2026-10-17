# Build helpful, trustworthy agents into your application

> **Security scope:** These practices address agent behavior and do not make an application secure. Authentication, authorization, encryption, transport security, and other application security controls require separate design and review under your organization’s security policies.

An agent can help people use capabilities they cannot find, understand unfamiliar workflows,
and carry out work with them. Making that assistance useful takes more than a chat box:
the agent needs a connection to the real application, appropriate authority, and evidence
that it understands and helps.

This guide explains how to build that connection. It is for developers, architects, and
product people adding an agent to an application or website—or improving one they already have.
A small TodoMVC-style application makes the design concrete without requiring you to learn
a complicated business domain. Managing todos is the teaching example, not the reason to build an agent.

Follow the chapters from motivation and design through the working sample and evaluation,
or use the chapter navigation to go directly to what you need.

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
