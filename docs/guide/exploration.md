# Explore the experience

Fixed cases tell you about questions you already thought to ask. Exploration finds questions
you missed. Start by using the application yourself: combine requests, change your mind,
refer to tasks indirectly, and compare the explanation with the screen and saved state.

## Start with a person

![A person explores task merging and a request containing several tasks.](../images/exploratory-tester.png)

The exploratory tester gives you a separate test list. Use it to test the interaction without
changing your own list. Do not treat an awkward answer as automatically wrong: decide whether
it accomplished the person's request and communicated accurately.

## Broaden the exploration with personas

Human testers may have difficulty thinking of new scenarios or may repeat familiar ones. A persona is another
model playing a person with a situation and goals. Sam demonstrates automated exploratory
testing, not a claim that people need an agent to manage a simple todo list.

![Sam explores cleanup and filtering while deletion requests wait for approval.](../images/persona-sam.png)


Set `EVALBASICS_PERSONA_PLAYER=true` in `.env` to show the visible player without enabling
trace export (the sample configuration includes it). It lets you watch a persona interact
with the actual screen. Pick a persona, then use Next or Play to watch. Each persona
uses a separate test list; pick None to return to your own list. The command-line runner uses the same persona prompts,
screen description, and approval actions, with a separate separate test list for each session:

```bash
.venv/bin/python -m evaluations.personas --persona sam --turns 8 --max-tokens 50000
.venv/bin/python -m evaluations.personas --replay runs/personas/RECORD.json
```

The first command makes paid calls for the persona, application agent, and claim judge.
It saves JSON checkpoints throughout the conversation and creates a standalone HTML review
beside the record. The second command regenerates that review without making model calls.
Use Previous/Next to inspect the recorded conversation, approval clicks, and state changes.
It does not rerun actions or reproduce the visual interface. Older persona JSON records
can also be reviewed; evidence they did not record is identified as missing.

`--max-tokens` is shared across all selected personas and all three model roles.
It stops further calls after reported usage reaches the allowance;
a call already underway can exceed it. Missing usage stops further calls too. This is
**not a hard dollar billing cap**; provider retries and charges without returned usage may
not be measurable locally. Choose a small turn limit for an initial exploration.
Ctrl-C retains the latest checkpoint. A record left with status `running` after a forceful
termination is incomplete, not a successful session.

Langfuse is an optional example integration, not a requirement or recommendation over other
tools. Headless exploration exports no traces unless you add `--trace` and configure your
own project keys. Local records and HTML review work without a Langfuse account or server.
The Python dependencies still include its SDK. Ordinary application chats are not exported.

Persona frustration and judge warnings are **candidate findings for human review**, not
fixed-suite failures. Review flagged conversations and a sample of apparently successful ones,
decide whether they expose a real problem,
then add a regression case and a separate held-out variant. Do not mix exploratory persona
sessions into the fixed-suite control chart. Headless exploration does not verify rendering,
layout, or interaction through actual browser controls; the visible player remains valuable.


## Turn observations into evidence

The persona returns structured fields for messages, approval choices and reactions; the
[walkthrough explains the turn format](../guides/walkthrough.md#how-a-persona-takes-a-turn).
Satisfaction is the simulated person's opinion, not proof that the application worked.

Review flagged findings and sample apparent successes. When people disagree, put the exact
request, starting state and proposed action for a reviewer to inspect. Ask a focused question:
“Did the user uniquely identify this task?” or “Were other items requested too?” Preserve
the original record and the corrected judgment; a reviewer's first mistake is not a target
for the system to imitate.

![A focused human review of a request and proposed action.](../images/human-review.png)

Confirmed problems become repeatable regression cases, with separately held-out wording to
check that a fix generalizes. Next, [evaluate the outcome systematically](../principles/evaluating-agents.md).
