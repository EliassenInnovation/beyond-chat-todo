<span id="apply-the-approach-to-your-application"></span>

# Apply it to your app

Choose one useful job people struggle to complete. Write down the starting state, what the
person is trying to achieve, what must change, what must remain unchanged, and what confirmation
they need. Include examples of asking for instructions as well as asking for action.

## Choose work worth improving

Use support-call reasons, abandoned tasks and user research to identify common or costly jobs. Compare the agent with the help and controls people already have. Early evidence may be a useful new workflow; as adoption grows, measure completion, corrections, time saved, support effort and cost per completed job.

Improve an existing application one job at a time. Trace the current behavior, including unwritten rules that need a domain expert, record it in tests, and move it into shared application code. Functional behavior should remain stable even when unit tests must change with the internal structure. A coding agent can trace code and draft checks; people supply business rules that were never recorded.

## Make one operation shared

Find the existing business operation behind the UI and connect the agent to it, following
[Start with shared operations](design.md#start-with-shared-operations). Do not implement a
second version for chat.

Decide the authority of each caller explicitly, using
[Enforce policy and approval](authority.md#enforce-policy-and-approval). Do not copy the
sample's deletion policy without considering your domain.

## Give the agent current data and useful tool results

Describe the relevant view and controls, provide tools that read current data, and return facts from execution.
Keep the prompt focused on the agent's job and priorities. Let tools describe their inputs,
results and limits; let code own rules, arithmetic and saved-state facts.

When a case fails, inspect the capability, context, data and feedback before adding another
sentence to the prompt. An absent operation or stale screen description is not repaired by
asking the model to be more careful. Fix a class of requests and test different wording.

## Test the job and review the results

Start with offline tests for authority, validation, recovery, and atomicity: a change
succeeds completely or leaves data unchanged. Add visible evaluation cases for ordinary
jobs, ambiguity, and realistic mistakes. Review correct and incorrect
answers when checking a judge. Explore with people and personas, then preserve confirmed
findings as cases. Keep held-out cases separate from development.

Run focused evals while changing a capability, then a broader suite before accepting it.
[Everyday checks are not a new baseline](../guides/evaluation-results.md#everyday-checks-are-not-a-new-baseline)
gives the schedule and explains when a change starts a new comparison period.

## Keep a record of attempted work

A trace helps explain how a model reached a result. An application audit record answers a
different question: what was requested, what was allowed or refused, and what actually changed?
Record the caller, operation, relevant versions, result and necessary review evidence at the
execution boundary. Protect sensitive data and decide access and retention deliberately.

Undo should add evidence of a reversal rather than erase the original action. Check the
record against actual outcomes in tests. The Todo sample's local evaluation records help illustrate
inspection; they are not a durable production audit service.

## Extend to other interfaces deliberately

The same capability contract can support a command line, an API or an MCP adapter. MCP—the
Model Context Protocol—lets an external agent discover and call tools, potentially combining
capabilities from several applications. That does not replace each application's authority checks.

Decide which operations make sense for each interface. Highlighting a control only helps a
caller sharing that screen. A data read may be useful externally without needing to be offered
to the embedded agent. Tool listing and permission to execute remain separate decisions.
Across applications, also establish identity, consent, data movement and recovery when only
some steps succeed. The Todo sample does not implement an MCP server or cross-app workflow.

## Decide which mechanisms to add

The guide describes more mechanisms than most applications need. Every agent that changes
data needs shared operations, permissions and approval enforced in application code,
confirmations written from the saved result, offline tests of those rules, and a few
evaluation cases that check the outcome. For each further mechanism, answer five questions:

1. What does an error cost, and would the person see it and be able to undo it?
2. How often do people do this job, and how much depends on it?
3. How many steps, records and screens does the workflow involve?
4. Would a deterministic check, an explicit selection on the screen, or a confirmation
   prevent the same error?
5. Do recorded failures show that the simpler version makes this error?

Add a mechanism when the answers meet the condition in the third column of this table.

| Mechanism | What it costs | Add it when | Until then |
| --- | --- | --- | --- |
| [Model-based intent guard](authority.md#decide-whether-a-guard-is-needed) | A model call before each guarded action, some clear requests refused, and labeled cases to evaluate it | Evaluations show the agent acting on the wrong item, the error is hard to notice or undo, and validation cannot catch it | Validate inputs, return the candidates when several records match, and ask the person |
| [Answer check](evaluation.md#decide-which-failures-to-prevent-before-showing-a-reply) before a reply is shown | A model call and a delay on each checked reply, and some good replies stopped | A wrong reply would break a policy or mislead the person about something consequential | Show application-written text for facts and measure reply quality in evaluation |
| [Personal context and onboarding](onboarding.md) | Stored personal data, with rules for saving, correcting, removing and reading it | The right answer differs from person to person and the application lacks the facts | Use the data the application already holds and ask during the conversation |
| [Screen state and screen actions](screen.md) | One owner for each piece of view state, declared controls, and tests for both | People ask about what they are looking at, or ask to be shown or taken to a control | Give the agent data tools only |
| [Audit records](authority.md#record-changes-and-make-undo-safe) | Storage, access rules and a retention policy | The agent changes data other people rely on, or policy requires a record of who changed what | Keep the change history that undo needs |
| [Tracing](../guides/langfuse.md) | A tool to run, and conversation data held in a second place | A report does not explain a failure and you need the exact model input | Read the local run records and reports |
| [Records for references to earlier results](../reference/conversation-references.md) | Additional saved records to maintain | People revise or undo earlier multi-step work, and evaluations show the conversation history is not enough | Keep the person's words, tool calls and results in the history |
| [Persona testing](exploration.md#broaden-the-exploration-with-personas) | Model calls for each simulated conversation, and human review of the findings | Fixed cases pass but people still meet problems, or conversations run for many turns | Explore the application yourself and add a case for each confirmed problem |
| [Baselines and control charts](../guides/evaluation-results.md) | 20 or more comparable full runs on a fixed configuration | The same suite runs repeatedly on an unchanged version and you need to separate ordinary variation from a change | Read every failure, repeat the affected cases, and compare old and new results case by case |

Record the mechanisms you set aside and the reason. Reconsider one when its answers change,
for example when a new job has costlier errors or evaluations start showing the error.

## Use this guide with a coding agent

Give the agent the complete guide and access to the application it will assess. Begin by
asking it to connect the principles to the existing architecture and your priorities.
For example:

> Read this guide and inspect our application. Trace a representative request through the
> UI, application operations, validation, permissions, storage, and feedback. Explain which
> parts of the approach we already support, which principles would help with our goals,
> and what tradeoffs or open questions need our decision. Use code references and distinguish
> implemented behavior from behavior verified by tests. Propose an incremental architecture
> and implementation plan, with acceptance checks adapted to our application. Start with
> assessment and a proposal; we will agree on the implementation scope together.

For a new application, ask for a proposal for which code handles each responsibility, and a first complete operation
instead of a trace through existing code. In either case, record the choices you adopt,
adapt, or set aside and why. The Todo code demonstrates implementations the agent can
inspect; the examples provide starting points for your application's design.

Use the [acceptance checks](../principles/implementation.md) to verify the agreed behavior.
[Reassess added mechanisms after substantial model changes](../guides/evaluation-method.md#reassess-added-mechanisms-after-substantial-model-changes),
and simplify when evaluation shows the intended behavior is preserved.

## Write a brief for the first change

!!! practice "Practice — write a first implementation brief"
    Use the same application and job you chose earlier. Write a short brief naming:

    - The person's situation and desired outcome.
    - The existing operation to share, or the workflow that needs one owner.
    - The context the agent needs and the authority of each caller.
    - The outcome, recovery and communication checks you will run.
    - The first person who will try it and the evidence you will review before expanding it.

    Keep the scope to one useful job. Mark unanswered questions rather than filling them
    with assumptions. Use the [acceptance checks](../principles/implementation.md) to review that scope.

Use the [checklist builder](checklist-builder.md) to record those decisions and download
persistent instructions plus detailed checks. Presets suggest a starting scope; review the
remaining checks and note adaptations or reasons for setting them aside. The full guide
remains available as a separate download.

## Check what the sample does not provide

This is a local, single-user teaching app. Production work may require authentication,
isolation between customers' data, concurrency control, durable audit records, operation IDs, safe retries,
retention policy and deployment security. A model guard does not supply those guarantees.
The [sample assessment](../guides/sample-assessment.md) documents these limitations.

Use the [acceptance checks](../principles/implementation.md) for a scoped review, not as a
claim that every check applies to every product. State what you implemented, what evidence
you collected, what remains uncertain, and which limitations matter to the user.

The goal is useful assistance with safeguards that match the consequences of a mistake.
An application can be useful before it is perfect. Before release, investigate failures
and support claims about its behavior with evidence.
