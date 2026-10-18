# Onboarding, when needed

Some applications need to understand the person before they can provide useful personalized
assistance. A financial application needs context about goals, circumstances, and when the
person expects to use their money. A personal shopper needs preferences, sizes, and budget
to recommend something suitable. An established user may already have that information
recorded in the application. For a new user, onboarding can help gather it.

The purpose is to learn enough to help with the person's questions. Completing a profile
is not the objective.

## Help the person get started

A setup wizard can ask people to make decisions before they understand why those decisions
matter. Someone who came to accomplish a task instead faces several screens of questions.
“Skip for now” may leave them wondering what will fail, what they are giving up, and how
hard it will be to complete setup later.

![A person hesitates over Skip for now in a seven-step setup wizard.](../images/wizard-frustration.png)

*“Can I skip this and do what I came here to do?”*

Conversational onboarding takes a different approach: begin with what the person wants to
accomplish, and ask for relevant information along the way. Explain why a question matters.
Use information already available in the application rather than asking the person to
repeat it. Microsoft's human–AI interaction guidelines support assistance that is relevant
to the current task and timed to the person's context.
[Microsoft: Guidelines for Human-AI Interaction](https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/)

## Learn just enough

Advisor, a separate investment application, illustrates this approach. Its built-in coach
addresses the user's request first, then may ask at most one setup question. Four facts
are treated as core: age, retirement plan, goals, and comfort with risk. Other information
can be learned as it comes up. These are Advisor's choices, not a universal onboarding list.

Ask for only the precision the assistance needs. An age can be enough without a birthdate.
“Early retirement” or “around the usual age” may be sufficient unless the person has a
specific goal requiring more detail. Uncertainty is useful information too; do not turn
an approximate answer into an exact date or a definite commitment.

In one simulated conversation, Maya describes financial independence as a goal, with a
flexible hope of retiring early. The coach records that as an aspiration rather than a
fixed date. It asks about her comfort with losses, preserves her uncertainty, and follows
her questions about how the accounts fit her plans. Later replies use that context. The
point is that what it learns contributes to the assistance, not that it fills every field.

## Save what the person actually said

Onboarding needs somewhere in the application to put what it learns. Advisor added
“Facts about me,” available through its UI, CLI, built-in agent, and MCP server. These are
shared application data, rather than facts left only in a conversation. People can ask what
the application knows about them and correct or remove information.

Advisor permits the coach to record clear personal facts without a separate approval for
each one. “I am 54” can be saved directly. “Retiring early might be nice” is tentative and
should not become an established retirement goal. If a goal includes a condition, preserve
it. If the person clarifies or changes a goal, update the saved information.

Keep the scope of the statement too. Being uncomfortable with one holding is not necessarily
an expression of comfort with risk across all investments. A separate model-based write
check reviews proposed coach saves against the conversation; it supplements capability
validation. Settings and rules still require the appropriate user direction.

External MCP agents use the same saved data and capability validation, but do not receive
that conversation-based check: Advisor's server does not see their conversations. Shared
capabilities do not mean every caller receives identical context or safeguards.

## Let application state guide the questions

Advisor uses one coach prompt, with onboarding rules that apply according to state supplied
by the application. Code derives that state from saved data and the facts declared by its
capabilities. The coach does not have to remember which facts it collected in a previous
conversation; it receives the current state on each turn.

Setup questions stop at the first of three points: the four core facts are known, the person
asks to stop, or three conversations have passed without completing the core facts. The
person can ask to resume. These limits keep onboarding from becoming the purpose of every
conversation. They do not mean that four facts are enough for every subsequent request;
a particular task may still require additional information.

The design uses [shared application capabilities](design.md): application code owns
the stored facts and progress, while the agent chooses how to converse within those rules.

## Check the assistance, not just the profile

Test whether the agent answers the person's questions, records accurate information at the
right scope, and uses that information appropriately later. Include new users with little
saved context and established users with populated application data. Keep a simulated user's
private background separate from what the application has learned.

The Advisor examples have been exercised with simulated users. Those runs can reveal
incorrect saves, unnecessary precision, or questions that displace the user's task. They
cannot establish that real users find gradual onboarding natural or less intrusive. That
requires observing people use it, including whether they reach a useful result and understand
why information is requested. More facts collected is not sufficient evidence of better help.

!!! consider "Consider — what does the agent need to know?"
    Choose one task. Which facts about the person materially affect the assistance? What
    does the application already know? Write one question that would help with the current
    task, and explain why its answer matters. Leave unrelated profile fields for later.

