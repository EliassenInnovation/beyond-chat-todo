# Learn about me

Useful assistance often depends on knowing something about the person. A financial
application needs context about goals, circumstances, and when the person expects to use
their money. A personal shopper needs preferences, sizes, and budget. What matters depends
on the job the person wants to accomplish. A shopper who mentions an upcoming wedding gives
the application a reason to learn the dress code and budget for that occasion.

That understanding develops over time. Someone may arrive with data already in the
application, share a preference while asking a question, or change a goal after months of
use. The application needs a way to learn, retain, and revise the information that improves
its assistance.

The Todo sample has no personal profile or onboarding. The implementation examples in this
chapter come from Advisor, a separate investment application.

## Onboarding, when needed

Onboarding helps a new person begin using the application. They may need useful help
before the application knows much about them. This initial setup can gather a few facts
that affect many requests.
Start with what the person came to do, use the information already available, and ask for
what would make the next answer more useful.

### Ask during the task

A setup wizard can ask people to make decisions before they understand why those decisions
matter. Someone who came to accomplish a task instead faces several screens of questions.
"Skip for now" may leave them wondering what will fail, what they are giving up, and how
hard it will be to complete setup later.

[![A person hesitates over Skip for now in a seven-step setup wizard.](../images/wizard-frustration.png)](../images/wizard-frustration.png)

*"Can I skip this and do what I came here to do?"*

Conversational onboarding takes a different approach: begin with what the person wants to
accomplish, and ask for relevant information along the way.
Use information already available in the application rather than asking the person to
repeat it. Microsoft's guidelines for human-AI interaction support assistance that is relevant
to the current task and timed to the person's context. [Microsoft: human-AI interaction guidelines](https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/)

### Ask only for what the assistance needs

Advisor illustrates this approach. Its built-in coach
answers the person's request first, then may end the reply with one setup question. It asks
about each fact at most once in a conversation. Four facts are treated as core: age,
retirement plan, goals, and comfort with risk. Other information can be learned as it comes
up. Choose the core facts according to the assistance your application provides.

Ask for only the precision the assistance needs. An age can be enough without a birthdate.
"Early retirement" or "around the usual age" may be sufficient unless the person has a
specific goal requiring more detail. Preserve uncertainty as part of the answer, including
whether a goal is tentative or a date is approximate.

In one simulated conversation, Maya describes financial independence as a goal, with a
flexible hope of retiring early. The coach records that as an aspiration rather than a
fixed date. It asks about her comfort with losses, preserves her uncertainty, and follows
her questions about how the accounts fit her plans. Later replies use that context.

### Let application state guide the questions

Let code derive onboarding progress from saved data and the facts declared by application
capabilities, and supply that state to the agent. Set limits on setup questions and give
the person a way to stop or resume them. A later task may still need additional information.

!!! example "How Advisor does it: setup questions"
    Advisor supplies the current onboarding state on each coach turn. Setup questions stop
    when any of three conditions is met: the four core facts are known or declined, the person
    asks to stop, or three app sessions have passed without completing the core facts. A session
    counts when the person sends a message; it does not mean a separate saved conversation.
    The person can ask the coach to stop or resume setup questions, and an external
    MCP agent can do the same through the onboarding guidance and tools Advisor's server
    provides. There is deliberately no on-screen control.

The design uses [shared application capabilities](design.md): application code owns
the stored facts and progress, while the agent chooses how to converse within those rules.

## Save what the person actually said

The application needs a place to keep what it learns. Make saved information available for
people to inspect, correct, or remove.

Record clear statements together with any conditions or uncertainty the person expressed. Keep tentative wishes tentative, preserve
conditions attached to goals, and update information when the person clarifies it. Keep the
statement's scope: a budget for one wedding belongs to that occasion until the person says
it applies more broadly.

Decide which statements authorize a save and which changes need explicit agreement. Show a
receipt when a save is not already visible, and give the person a way to undo it.

Advisor keeps this information in "About you," available through its screen, command line,
built-in agent, and MCP server.

[![Advisor's About you panel showing age, retirement plans, events, and saved personal context, with controls to edit or remove information.](../images/advisor-about-you.png)](../images/advisor-about-you.png)

*Advisor's "About you" panel makes saved context available for review and correction.
The person can edit or remove information as their circumstances change. Select the image
to view it at full size.*

Advisor permits the coach to record clear personal facts without a separate approval for
each one. "I am 54" can be saved directly. "Retiring early might be nice" remains tentative.
Discomfort with one holding is recorded as a concern about that holding only. A separate model-based guard, which Advisor calls its write check,
checks each proposed coach save against the conversation; it supplements capability
validation. Settings, limits, and rules need an explicit request; a "yes" to a specific
offer counts. The write check enforces this, and if the check is unavailable, nothing is
saved. Coach saves show a receipt unless already visible, and can be undone.

!!! example "How Advisor does it: external agents"
    External MCP agents use the same saved data, schema and capability validation, audit log,
    and undo. The write check and guards need the conversation, which Advisor's MCP server never
    sees, so they do not apply to external writes, and the application shows no receipt for
    them. This is a known limit of the external path. Shared capabilities do not mean every
    caller receives identical context or safeguards.

Saved facts are personal data. In Advisor, external MCP clients can read them as well as
the coach, and the audit log records saved values and, by default, the conversation. Decide
which callers can read these facts, what your application records, and how long it keeps it.

## Keep learning as the person uses the application

Later tasks can reveal new preferences or changes in circumstances. A shopper who previously
wanted formal clothes for office visits may now need them for an outdoor wedding. Keep the
occasion's requirements separate from lasting preferences, and revise saved information when
the person says their preferences have changed. Future conversations should start from that
current understanding.

When an answer depends on saved information, check whether that information is still current.
Code can supply when a record was last confirmed and how much time has passed. The agent can use the person's
request to decide whether to check it. Before recommending an outfit, a shopper might check
whether an earlier budget applies to this wedding. Looking up the delivery date for an
existing order usually needs no such question. Similarly, asking whether to keep an
investment may require checking the saved reasons for owning it; asking its current value
usually does not. The time since information was confirmed is a reason to consider a
check, rather than proof that it has changed.

Give each kind of saved information a way to record when the person last confirmed it,
including confirmations that leave the value unchanged. Code can then supply that date and
the elapsed time alongside the information. Guidance should explain when a check would help
the current task. Make the connection understandable: "Does the budget we used last time
apply to this wedding too?"

Once the person answers, use that response in the current task and future assistance.

## Test whether learning improves the assistance

Test whether the agent answers the person's questions and records accurate information at
the right scope. Include new users with little saved context and established users with
populated application data. Keep a simulated user's private background separate from what
the application has learned. Advisor's evaluation cases include a tentative retirement
wish that must not be saved as a plan, and a feeling about one holding that must not be
saved as comfort with risk.

Test the whole sequence: a fact is stated, saved accurately, used in a later conversation,
then confirmed, corrected, or removed. The later response should reflect the updated
information. Test, including in longer conversations, whether the agent avoids repeating a
question after an answer or refusal, and what new evidence should prompt another check.

The Advisor examples have been tested with simulated users. Those runs can reveal
incorrect saves, unnecessary precision, or questions that interrupt the user's task. They
cannot establish that real users find gradual onboarding natural or less intrusive. That
requires observing people use it, including whether they reach a useful result and understand
why information is requested. Measure whether the learned context improves the help,
alongside the accuracy of the saved facts.

!!! consider "Consider — what does the agent need to know?"
    Choose one task. Which facts about the person change the assistance needed? What
    does the application already know? Write one question that would help with the current
    task, and note what its answer would change. Leave unrelated profile fields for later.

Next, [define authority and recovery](authority.md) for the actions the agent may propose.
