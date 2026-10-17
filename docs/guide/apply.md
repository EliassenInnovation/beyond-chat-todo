# Apply the approach to your application

Choose one useful job people struggle to complete. Write down the starting state, what the
person is trying to achieve, what must change, what must remain unchanged, and what confirmation
they need. Include examples of asking for instructions as well as asking for action.

## Make one operation shared

Find the existing business operation behind the UI. If its rules live in an event handler,
move them behind a shared boundary and keep the existing behavior under tests. Connect the
agent to that operation; do not implement a parallel version for chat.

Decide the authority of each caller explicitly. Ask whether the action has consequences
the application cannot undo, whether approval is justified, and how to bind that approval
to the exact proposal. Do not copy the sample's deletion policy without considering your domain.

## Supply the evidence the agent needs

Describe the relevant view and controls, expose fresh reads, and return facts from execution.
Keep the prompt focused on the agent's job and priorities. Let tools describe their inputs,
results and limits; let code own rules, arithmetic and saved-state facts.

When a case fails, inspect the capability, context, data and feedback before adding another
sentence to the prompt. An absent operation or stale screen description is not repaired by
asking the model to be more careful. Fix a class of requests and test different wording.

## Build a small body of evidence

Start with offline tests for authority, validation, atomicity and recovery. Add visible eval
cases for ordinary jobs, ambiguity and realistic mistakes. Review correct and incorrect
answers when checking a judge. Explore with people and personas, then preserve confirmed
findings as cases. Keep held-out cases separate from development.

Run focused evals while changing a capability, then a broader suite before accepting it.
Repeated baseline collection serves a different purpose: estimating ordinary variation in
a fixed configuration. Changing the model, grader or cases requires a new comparison period,
rather than updating the old chart's limits without identifying the change.

## Keep a record of attempted work

A trace helps explain how a model reached a result. An application audit record answers a
different question: what was requested, what was allowed or refused, and what actually changed?
Record the caller, operation, relevant versions, result and necessary review evidence at the
execution boundary. Protect sensitive data and decide access and retention deliberately.

Undo should add evidence of a reversal rather than erase the original action. Check the
record against actual outcomes in tests. The todo's local evaluation records help illustrate
inspection; they are not a durable production audit service.

## Extend to other interfaces deliberately

The same capability contract can support a command line, an API or an MCP adapter. MCP—the
Model Context Protocol—lets an external agent discover and call tools, potentially combining
capabilities from several applications. That does not replace each application's authority checks.

Decide which operations make sense for each interface. Highlighting a control only helps a
caller sharing that screen. A data read may be useful externally without needing to be offered
to the embedded agent. Tool listing and permission to execute remain separate decisions.
Across applications, also establish identity, consent, data movement and recovery when only
some steps succeed. This todo sample does not implement an MCP server or cross-app workflow.

## Account for what the sample leaves out

This is a local, single-user teaching app. Production work may require authentication,
tenant isolation, concurrency control, durable audit records, operation IDs, safe retries,
retention policy and deployment security. A model guard does not supply those guarantees.
The [sample assessment](../guides/sample-assessment.md) makes the boundaries inspectable.

Use the [acceptance checks](../principles/implementation.md) for a scoped review, not as a
claim that every check applies to every product. State what you implemented, what evidence
you collected, what remains uncertain, and which limitations matter to the user.

The goal is useful assistance with safeguards proportionate to consequences. Perfection is
not a prerequisite for value; unexamined failures and unsupported claims are not evidence of readiness.
