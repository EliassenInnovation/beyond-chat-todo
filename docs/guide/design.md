# Design the connection

Start with the work your application already does. A **capability** is an operation with
meaning to the application: add an item, reschedule an appointment, or submit an order.
The UI and agent should use the same implementation, validation and data.

## Build the capability once

[![The UI and model tools sit above shared capabilities, grounded in users' jobs.](../images/shared-capabilities.svg)](../images/shared-capabilities.svg)

*Different interfaces reach one owner of each operation. Sharing implementation does not grant identical authority.*

Keep the screen's event handling and the model's tool adapter thin. Both reach the shared
operation. Otherwise, a rule fixed in the UI can remain broken in the agent's separate copy.
An existing service layer may already provide this boundary; you do not have to rebuild
an application before adding one useful capability.

Name tools for work people recognize. A tool per mouse click makes the agent reconstruct
the interface. A tool that changes any field can hide too much meaning. The useful boundary
is an operation with clear inputs, consequences, and a result the application can report.

## Keep three decisions distinct

| Decision | Owner | Example |
| --- | --- | --- |
| May this caller perform this operation? | Application code | An agent may propose deletion but may not approve its own request. |
| Does the proposed action fit what the person asked? | An evaluated intent guard | Has the person uniquely identified the task being changed? |
| Is the result good enough? | Tests, evals and human review | Did every requested change happen, and was the explanation accurate? |

A model-based guard can make mistakes. It supplements code-enforced authority; it cannot
replace it. The sample supports guards as a normal part of its design, with narrow questions
and explicit evidence. They are not temporary experimental switches.

## Match approval to consequences

A person may be permitted to place a trade through the UI while an agent can only propose
it for code-enforced approval. The shared capability still owns the operation.

**Todo deletion deliberately stands in for an irreversible action.** This teaches how to
handle consequential actions the application cannot undo, such as transferring money,
placing a trade, or deleting a repository. It is not included because the sample needs a
better Undo button. Ordinary todo deletion would rarely justify this gate; choose safeguards
for the consequences in your own product.

Bind approval to the actual proposed details. A changed task must not silently inherit an
old approval. Keep caller identity outside the model's arguments. The walkthrough shows
both controls in working code.

## Know what the person sees, and be able to change the view

[![Shared screen state connects the interface, the agent's observations and screen actions.](../images/screen-context.svg)](../images/screen-context.svg)

*Observation and control are separate needs. A filter changes the view without deleting hidden data.*

Give the agent current view state and the names of controls, alongside tools to point to or
operate them. In this sample that means a structured description of the active filter and
visible task IDs, not a screenshot or a claim to know every pixel in the viewport.
The UI and agent change the same view state through shared dispatch. A larger application
may need a state machine for navigation and multi-step interactions; this sample does not
pretend its small view object is one.

## Report facts from the application and plan for failure

Application code should report what actually changed. In the sample, code-written receipts
are delivered directly, followed by any additional model explanation. An eval checks the
receipts and judges the explanation separately; the model can still make a false claim.

Decide what happens if a batch fails, a save fails, or the provider stops after a successful
save. The sample demonstrates atomic local actions and recovery messages. It does not
provide durable operation IDs or safe replay of uncertain network writes. Those are explicit
limits to address when taking this design into a service.

Now [run the sample](start.md), then follow the same boundaries in the implementation.
