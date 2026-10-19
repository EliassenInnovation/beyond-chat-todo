# Onboarding, when needed

Some applications need to understand the person before they can provide useful personalized
assistance. A financial application needs context about goals, circumstances, and when the
person expects to use their money. A personal shopper needs preferences, sizes, and budget
to recommend something suitable. An established user may already have that information
recorded in the application. For a new user, onboarding can help gather it.

The purpose is to learn enough to help with the person's questions. Completing a profile
is not the objective. The todo sample does not include onboarding; the examples in this
chapter come from Advisor.

## Ask during the task instead of in a setup wizard

A setup wizard can ask people to make decisions before they understand why those decisions
matter. Someone who came to accomplish a task instead faces several screens of questions.
"Skip for now" may leave them wondering what will fail, what they are giving up, and how
hard it will be to complete setup later.

![A person hesitates over Skip for now in a seven-step setup wizard.](../images/wizard-frustration.png)

*"Can I skip this and do what I came here to do?"*

Conversational onboarding takes a different approach: begin with what the person wants to
accomplish, and ask for relevant information along the way. Explain why a question matters.
Use information already available in the application rather than asking the person to
repeat it. Microsoft's guidelines for human-AI interaction support assistance that is relevant
to the current task and timed to the person's context. [Microsoft: human-AI interaction guidelines](https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/)

## Ask only for what the assistance needs

Advisor, a separate investment application, illustrates this approach. Its built-in coach
answers the person's request first, then may end the reply with one setup question. It asks
about each fact at most once in a conversation. Four facts are treated as core: age,
retirement plan, goals, and comfort with risk. Other information can be learned as it comes
up. These are Advisor's choices, not a universal onboarding list.

Ask for only the precision the assistance needs. An age can be enough without a birthdate.
"Early retirement" or "around the usual age" may be sufficient unless the person has a
specific goal requiring more detail. Uncertainty is useful information too; do not turn
an approximate answer into an exact date or a definite commitment.

In one simulated conversation, Maya describes financial independence as a goal, with a
flexible hope of retiring early. The coach records that as an aspiration rather than a
fixed date. It asks about her comfort with losses, preserves her uncertainty, and follows
her questions about how the accounts fit her plans. Later replies use that context.

## Save what the person actually said

Onboarding needs somewhere in the application to put what it learns. Advisor added
"About you," available through its screen, command line, built-in agent, and MCP server.
These are shared application data, rather than facts left only in a conversation. People
can ask what the application knows about them and correct or remove information.

[![Advisor's About you panel showing age, retirement plans, events, and saved personal context, with controls to edit or remove information.](../images/advisor-about-you.png)](../images/advisor-about-you.png)

*Advisor's "About you" panel makes saved context available for review and correction.
The person can edit or remove information as their circumstances change. Select the image
to view it at full size.*

Advisor permits the coach to record clear personal facts without a separate approval for
each one. "I am 54" can be saved directly. "Retiring early might be nice" is tentative and
should not become an established retirement goal. If a goal includes a condition, preserve
it. If the person clarifies or changes a goal, update the saved information.

Keep the scope of the statement too. Discomfort with one holding says something about that
holding, not about the person's comfort with risk across all investments. A separate
model-based write check reviews each proposed coach save against the conversation; it
supplements capability validation. Settings, limits, and rules still need an explicit
request; a "yes" to a specific offer counts. The write check enforces this, and if the
check is unavailable, nothing is saved.

When the coach saves a fact, the application shows a short receipt, unless the change is
already visible on screen, and the person can undo the save.

External MCP agents use the same saved data, schema and capability validation, audit log,
and undo. The write check and guards need the conversation, which Advisor's MCP server never
sees, so they do not apply to external writes, and the application shows no receipt for
them. This is a known limit of the external path. Shared capabilities do not mean every
caller receives identical context or safeguards.

Saved facts are personal data. In Advisor, external MCP clients can read them as well as
the coach, and the audit log records saved values and, by default, the conversation. Decide
which callers can read these facts, what your application records, and how long it keeps it.

## Let application state guide the questions

Advisor uses one coach prompt, with onboarding rules that apply according to state supplied
by the application. Code derives that state from saved data and the facts declared by its
capabilities. The coach does not have to remember which facts it collected in a previous
conversation; it receives the current state on each turn.

Setup questions stop at the first of three points: the four core facts are known or
declined, the person asks to stop, or three conversations have passed without completing
the core facts. A conversation is one session in the app in which the person sends a
message. The person can ask the coach to stop or resume setup questions, and an external
MCP agent can do the same through the onboarding guidance and tools Advisor's server
provides. There is deliberately no on-screen control. These limits keep onboarding from
becoming the purpose of every conversation. They do not mean that four facts are enough
for every subsequent request; a particular task may still require additional information.

MCP hosts such as the Claude desktop app keep the tool list and server instructions they
received when they connected. After a server adds or changes tools or instructions, restart
the host so external agents receive them.

The design uses [shared application capabilities](design.md): application code owns
the stored facts and progress, while the agent chooses how to converse within those rules.

## Test whether onboarding improves the assistance

Test whether the agent answers the person's questions, records accurate information at the
right scope, and uses that information appropriately later. Include new users with little
saved context and established users with populated application data. Keep a simulated user's
private background separate from what the application has learned. Advisor's evaluation
cases include a tentative retirement wish that must not be saved as a plan, and a feeling
about one holding that must not be saved as comfort with risk.

The Advisor examples have been exercised with simulated users. Those runs can reveal
incorrect saves, unnecessary precision, or questions that displace the user's task. They
cannot establish that real users find gradual onboarding natural or less intrusive. That
requires observing people use it, including whether they reach a useful result and understand
why information is requested. More facts collected is not sufficient evidence of better help.

!!! consider "Consider — what does the agent need to know?"
    Choose one task. Which facts about the person materially affect the assistance? What
    does the application already know? Write one question that would help with the current
    task, and explain why its answer matters. Leave unrelated profile fields for later.
