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

A person asks Advisor's coach for a Treasury ladder that pays out each month. Advisor
returns schedule A. The person says "keep everything to 12 months or less." The coach
sends this revision, with `A` standing for the earlier result's ID:

```json
{
  "based_on": "A",
  "changes": {"max_term": 12}
}
```

Advisor carries forward the earlier inputs, applies the shorter maximum term, validates
the complete set, and recalculates. If this changes the plan, it returns schedule B with
its own ID and reports the effective difference. Schedule A remains available for comparison.
A correction that already matches the plan returns the existing result marked unchanged.

These are Advisor's field names; Todo has no saved calculations. Advisor accepts exactly
one of three request shapes: `inputs` for a new plan, `based_on` plus `changes` for a
revision, or `result_id` for retrieval. Code rejects mixed shapes and either revision field
on its own. An existing scenario or calculation model in your application may already
provide the necessary state.

Advisor's results are immutable and addressed by ID within the caller's owner and workspace.
Each revision names the result it changes; there is no "latest result" lookup. Results
expire after 90 days, and each scope holds at most 500. A full store refuses new results
while preserving live ones. The schedule is a calculation: revising it changes no portfolio
setting and places no order.

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
