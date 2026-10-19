# Support references to earlier work

People return to previous topics with phrases such as "undo that" or "try six years."
The [request chapter](../guide/requests.md#interpret-follow-up-requests) explains the principle:
preserve the original words, actual tool calls and results, and relevant state so the agent
has evidence for interpreting the reference. Ask when materially different meanings remain.

## Start with the records the application already has

The model interprets the reference. Application code checks the selected object or operation,
its current permissions, and the validity of the requested change. Keep the original request
separate from the agent's interpretation so a later correction can recover from a wrong turn.

Todo illustrates this at a small scale. Its [task operations](../../todo/todos.py) return
structured results, and its [agent runtime](../../todo/agent.py) retains conversation and tool
history. The agent records the list before each request and checkpoints the request's changes
as one undo entry. These are the implementation examples
available in this repository.

## Group related changes when recovery needs it

A request may change three due dates and move two tasks. An application can associate those
operations with a request or action-group identifier. "Undo that" can then refer to the group.
Code checks which operations completed, whether later edits affect recovery, and what can
safely be reversed.

Decide separately whether the group commits atomically and whether one Undo reverses the
whole group. Several separately committed operations can still belong to one undo group.
Explain partial recovery when some effects cannot be reversed. Todo demonstrates request-level grouping with its before-turn list state and a single
checkpoint. A named group with per-operation outcomes and recovery across later edits is
a further design choice for workflows that need it.

## Revise a saved calculation when reproducibility matters

Suppose a person asks for the payment on a $30,000 loan over five years, then says "try six
years." Carry forward the amount and interest rate, change the term, and calculate again.
An application may retain those inputs with a result identifier. One illustrative request is:

```json
{
  "based_on": "calculation-42",
  "changes": {"term_years": 6}
}
```

`based_on` identifies the earlier calculation; `changes` supplies the revised inputs.
These field names are an example, not Todo tools. An existing scenario or calculation model
may already provide the necessary state.

Resolve the selected result under current access rules, combine the revised inputs, validate
the complete set, and calculate a new result. Preserve the earlier result for comparison.
Identify the effective inputs and source dates so a person can understand what changed.
When using dated source data, make refreshing that data an explicit choice. A hypothetical
calculation remains a calculation until the person requests an application change.

## Check references across a conversation

Give retained records an appropriate owner, scope, and lifetime. Test missing, expired,
inaccessible, or deleted references, several possible subjects, and a return to an earlier
topic after unrelated discussion. An identifier helps locate a record; the application
still checks permission to use it.

Adapt [Checks 2.8–2.9](../principles/implementation.md#2-help-users-finish-the-job) to the
features you adopt. Judge reference resolution, the resulting application state or
calculation, and the explanation separately.
