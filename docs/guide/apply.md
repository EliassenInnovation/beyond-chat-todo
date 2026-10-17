# Apply the approach to your application

Choose one useful job people struggle to complete. Write down the starting state, what the
person is trying to achieve, what must change, what must stay unchanged, and what confirmation
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
not quietly moving the old chart's limits.

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
