<span id="evaluate-the-users-outcome"></span>

# Evaluate outcomes

[![The cycle from a user job through cases, measurement, review and improvement.](../images/improvement-loop.svg)](../images/improvement-loop.svg)

How do you know the agent helps users—and keeps working as you change it?
An **evaluation**, often called an **eval**, checks how the agent handles a user request
from a defined starting situation. It checks both the response and the changes made
against criteria for success.

A tool can execute correctly while changing the wrong task. A fluent answer can omit half the request. Evaluate the person's request, the actions, the saved result and the delivered answer together.

Use three kinds of evidence:

- Deterministic tests: code checks of application rules, with the same expected result each time.
- Scripted conversations: repeated measurements of known jobs.
- Human or persona exploration: testing situations you have not anticipated.

Keep their results separate. Persona satisfaction and reviewer opinions help identify what
to investigate; they are not pass/fail verdicts from the fixed evaluation suite.

If you already write software tests, retain them. Code can establish that an operation
validates and saves correctly. An **evaluation case** adds a starting situation, a user request
and criteria for the whole interaction. Repeating it measures how reliably the model chooses
and explains the right work. A **judge** is a model used to assess language against those
criteria; it is part of the measuring system and also needs checking.

## Define success before judging it

Check every part of the request, what must remain unchanged, and what the person needs to know. Record whether the user had to correct a mistake even if the final state is right. A necessary question about an ambiguous request is not such a correction.

Fail responses for meaningful problems: incorrect claims, unauthorized changes, omitted work or misleading next steps. Do not fail a reasonable answer merely because it differs from preferred wording. When reasonable people disagree, show the exact request, starting state, action and answer; resolve the criterion before tuning a model to satisfy it.

Use code for saved state, identifiers, arithmetic, permissions and delivery of application-written receipts. Use model judges for judgments that require interpreting language. Do not ask a judge whether the agent copied text that application code should have delivered directly.

!!! practice "Practice — judge the whole request"
    A person says, "Show overdue tasks first, and remove the completed ones." The app shows
    all active tasks without distinguishing overdue ones and creates deletion proposals for
    completed tasks. The reply says the deletions await approval.

    Write a verdict for each part: overdue priority, completed-task removal, and accurate
    reporting. What evidence would you inspect before giving an overall verdict?

The deletion may correctly remain pending under the application's approval policy, and its
report may be accurate. Showing all active tasks has not addressed "overdue first." Inspect
the actual view, which tasks were proposed for deletion, and the policy before grading the
whole response. A correct statement about one part cannot make the other part complete.

<span id="what-to-evaluate"></span>

## Decide which failures to prevent before showing a reply

Some failures must never reach the user, such as an answer that breaks a policy or reports a change that did not happen; stop those in the application before the answer is shown. The checks that stop them can miss a failure or stop a good answer, so measure them like any other check. Others are matters of quality or style, such as an answer that is longer than it needs to be. Measure those in evaluation. Do not rewrite answers in production each time one falls short.

## How to judge

**Code runs the conversation and collects the evidence.** It records the state before and
after, the tool calls, and which text the application wrote. Code checks run first. Judges
then read the model's answer alongside that evidence. Label application-written text so
judges can distinguish it from the model's answer.

**Grade quality against the user's goal.** When a judge grades quality, it looks at relevance, specificity, permitted next steps, tone, and coherence against what the user wanted and knew. Require examples and reasons, so a person reading a score can find the turn in the conversation that caused it.

**Code combines the verdicts.** Code merges every verdict into one report and writes any feedback to the agent from a template, so the feedback the agent receives is fixed text that people have read and tested, rather than wording a judge chose. A wrong verdict can still choose the wrong template, which is one reason the judges themselves are checked against people.

**Ask a judge more than once only when its mistakes vary.** Asking the same judge several times and taking the majority answer reduces mistakes that change from one attempt to the next. It does not fix mistakes the judge makes every time; in studies of models answering questions, more votes made hard questions worse, because the wrong answer became more consistent. [Chen et al.: repeated model calls](https://arxiv.org/abs/2403.02419) So ask a judge several times and take the majority answer only when checking it against people shows its mistakes vary between attempts.

**Reduce repeated mistakes by changing the judge or its input.** Judges that compare two answers tend to favor whichever is shown first; for those, ask twice with the order swapped. [Zheng et al.: LLM-as-a-judge](https://arxiv.org/abs/2306.05685) For other repeated mistakes, judges from different model families help, [Verga et al.: judges and juries](https://arxiv.org/abs/2404.18796) though different models often share mistakes, including when they act as judges, [Kim et al.: correlated errors](https://arxiv.org/abs/2506.07962) so checking judges against people is still needed.

<span id="calibrate-the-judges"></span>

**Measure before choosing a judge model.** A narrow judge checks one failure type, such as
claiming a save that did not happen; a broader outcome judge can find omissions beyond
those checks. Compare candidates and combinations against human-reviewed examples of
acceptable and unacceptable answers, requiring evidence for each verdict. State whether
people labeled every example or reviewed a sample of model labels. Inspect false failures
and missed failures, and reserve separate examples for evaluating a changed judge. Compare
cost, response time, unavailable responses, and disagreement patterns alongside accuracy.

**Missing judgment is missing evidence.** Record an unreadable or unavailable verdict as ungraded. An attempt cannot pass until all required checks are complete. A known failure remains a failure even if another check is missing. Show graded, failed and incomplete counts with each score; missing evidence must not improve the apparent pass rate. Mark a release decision inconclusive when required evidence is absent. A required runtime guard that cannot answer must not let the protected change proceed.

**Keep exploratory feedback separate from grades.** Simulated users produce unscripted
conversations. A separate model can also give a human reviewer a second opinion about a
recorded conversation. Neither the persona's reaction nor that second opinion assigns a
pass or fail; the designated graders do that.

**Judges follow the same data rules as the agent.** Anything that reads a user's conversation must run on a provider the organization has approved to process that data, and prohibited data is removed before it reaches a judge.

## How to read the results

Read the recorded request, actions, and outcome before interpreting summary scores. Repeated
runs help distinguish ordinary variation from a change in behavior. Different failures have different consequences: an unauthorized action should not be averaged together with a minor issue in wording when deciding whether to release.

**Distinguish a defect from a change in the measured rate.** Investigate deterministic failures and serious individual incidents directly. For a stable set of evaluations whose results can vary between attempts, small differences between runs can be ordinary variation. Use control-chart signals to investigate changes in that process; a stable rate can still be unacceptable. Review and save a baseline that later runs cannot change, and mark changed models, tools, cases or graders as new comparison periods. See [evidence and variation](../guides/evaluation-results.md) for the chart, limits and practical testing schedule.

**A perfect score on a few attempts is weak evidence.** Many fixes are assessed with only
5 or 10 attempts at one case. A Wilson confidence interval estimates the uncertainty in a
measured pass rate. At 95% confidence, its lower bound is about 57% for 5 passes out of 5,
and about 72% for 10 out of 10. Those perfect observed scores still leave considerable
uncertainty. Treat a small before-and-after comparison as an initial indication. Confirm
the fix with more attempts or with held-out requests: cases not used to develop it.

**Report whether every attempt succeeds, where consistency matters.** A pass rate says how often one attempt succeeds. But a user who does the same job every week cares whether it works every time. pass^k measures that: whether all k attempts at the same job succeed. [Yao et al.: τ-bench](https://arxiv.org/abs/2406.12045) [Anthropic: demystifying agent evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) For jobs where consistency matters, report it beside the pass rate, and say what k was.

To calculate it, make n attempts at each job, k or more, and count the c that succeed; for that job, pass^k is the number of ways to choose k attempts from the c successes divided by the number of ways to choose k from all n, and the suite's pass^k is the average over its jobs.

Start every attempt from the same saved state, so one attempt cannot change what the next one finds.

**When variation itself is the problem, find its cause.** Sometimes the variation is the problem: a test case that passes about half the time, or an answer that is difficult to classify under the grading rule. More runs will not settle this. Find where the variation comes from before changing anything: the application may be unreliable at this job, the test environment may differ between runs, or the grader may disagree with itself. Fix the application when it is the source, and change the test case or the rule only when they are.

**Decide before the run what would block a release.** Before running the suite for a release, write down who decides, which failures block the release (such as an answer that reports a save that did not happen), what failure rate is accepted for the rest, and what makes a run inconclusive, such as too many ungraded judgments or a required check that did not run. Report cost and time for each completed job as well as for each model call: an agent that needs many calls to finish a job costs more than its cost per call suggests.

**Keep a record behind each reported improvement.** When a report says a change helped, link the claim to a short record of the experiment: what changed, the versions of the model and the application, which cases were run and how many attempts each, the grading criteria, the result, and what the experiment could not show. Without the record, nobody can check the claim later, including the people who made it.

<span id="how-to-keep-the-test-cases-honest"></span>

## How to keep test cases valid and independent

**Test one hypothesis at a time.** Treat each change as an experiment. State the hypothesis first: "Rewording the move tool will stop the agent from choosing the wrong position." Change only that, and keep everything else the same: the model, the starting data, the other tools, and the grading rules. Record what each run actually used, including the model that served each call and the application's version, so you can tell later whether anything else changed. Save each failure, not just the totals, so you can see which conversations improved or became worse. [Yao et al.: τ-bench](https://arxiv.org/abs/2406.12045)

**Run the suite with failures injected.** Real tools fail: a read fails, a save fails, a call times out. Run all the test cases with failures like these injected on purpose, and compare the result with a normal run. The agent should report each failure truthfully and recover where it can. In one published benchmark of 14 models, injected failures barely changed how often an agent succeeded at least once in three attempts, but cut how often it succeeded all three times by up to 24 percentage points. [Ye et al.: Claw-Eval](https://arxiv.org/abs/2604.06132)

**Retire test cases; never edit them.** Sometimes a test case turns out to be wrong: its expected answer was a mistake, or its script makes no sense. Do not fix it in place, because then earlier runs measured something different from later ones, and nobody can tell. Move it to a retired list with the reason, and add a corrected case under a new name.

**Use real conversations only after the organization has approved it.** Many companies record and analyze customer phone calls and learn a lot from them. They can do this because legal, risk, and compliance teams have decided how the recordings are captured, stored, and used, and who can see them, and because callers are told. Grading real users' conversations with an agent needs the same decisions, and users should get an explicit choice to opt in. Until those decisions are made, use only test data and synthetic conversations from simulated users. The cost is that a failure in real use reaches the team only when someone reports it or a simulated user happens to find it.

## Where evaluations live and who reads the results

The [Introduction's report and trace](../index.md#see-the-same-evidence) illustrate the
shared evidence: a person reads the interface, and a coding agent reads the underlying
records. Keep identifiers and links that let either point the other to the same interaction.
The [inspection appendix](../reference/inspection.md) gives an adaptable record format for
connecting offered tools, executed operations, and application outcomes.


**Keep evaluations in the repository and make their evidence inspectable.** A local report or an optional tracing tool such as Langfuse is a place to read what happened in a conversation and to compare runs. It is also a shared place where developers and their coding agents can inspect the same evidence: a person clicks through a conversation, an agent reads it through the tool's API, and either can point the other to the turn that matters. Keep the test cases, the graders, and the judges in the repository, and send copies to the tool rather than editing them there. Then if the tool became unavailable, the next run would still execute and grade, and you would lose only its screens. Moving to a different tool then means changing the code that sends records to it, not rewriting the evaluations. Tools in this field change quickly, and the evaluations should keep working when one is replaced.

**Read a sample of failed and successful cases.** Failures get read because someone has to fix them, but a passing case can hide a problem too: a check that is too lenient, or an answer that is right for the wrong reason. Read a sample of both. Inspect the exact model request as well as the answer: stale state, conflicting instructions and grader criteria that repeat a test answer can otherwise remain hidden.

**Make each conversation easy for a reviewer to read.** If you use a tool to record conversations between people and the agent, make sure each record carries the context a reviewer needs. The most important piece is the state after each turn: the list, the record, or the plan as the user saw it. Then the conversation reads in order: what was said, what the agent did, and what changed. Without it, a reviewer has to mentally reconstruct what the application looked like at each point. When the state is recorded, reviewers often notice that a change nobody asked for came from the turn before.

## Let a coding agent run budgeted experiments

Give a coding agent a defined scope and an evaluation budget to try improvements to prompts,
tool descriptions, and tool signatures. Let it inspect execution records, propose a change,
and compare the result with the baseline. Keep the evaluation procedure fixed during that
comparison and record each configuration and its results. Review changes to the judge as
separate experiments, using examples assessed by people.

This approach has research and engineering support. Anthropic describes using Claude Code
to improve tool implementations and descriptions from evaluation transcripts, with gains
checked on held-out tasks. GEPA studies prompt improvement through reflection on execution
traces and repeated evaluation. These results support the development method within the
settings tested. [Anthropic: improving tools with agents](https://www.anthropic.com/engineering/writing-tools-for-agents);
[GEPA](https://arxiv.org/abs/2507.19457).

Automated iteration can make the agent experience worse while improving its evaluation
score. A judge may reward unnecessary questions, longer replies, or steps that interfere
with the person's task. Research on prompt optimization has found that improvements can
be specific to the judge used during optimization.
[Elganayni and colleagues: judge-dependent prompt optimization](https://arxiv.org/abs/2604.20726).

Define successful outcomes, use code checks for what the application can verify, and
validate model judgments against human review of both passing and failing examples.
Watch complete interactions to assess the person's effort and the usefulness of the result.
Keep the best verified version available so unsuccessful experiments can be reversed.
Stop changing the fix before you run the [held-out cases](#check-that-a-fix-generalizes).
The [Todo walkthrough](../guides/walkthrough.md) explains how to run its visible and held-out
cases; [Check 6.9](../principles/implementation.md#check-6-9) applies the same separation to
automated optimization. Have someone outside the fixing session prepare the held-out cases.

## Scale testing to the change

Run offline checks and focused visible cases while developing a change, then the broader visible
suite before accepting a behavior change. Keep the fix unchanged while testing held-out cases,
following the separation described below. Record which cases ran so the evidence for the
change is clear.

Repeated baseline collection answers a different question: how much variation to expect
from a stable configuration. Use it when establishing or revisiting a baseline. The
[evidence chapter](../guides/evaluation-results.md) explains how that differs from checking
an individual edit.

## Reassess added mechanisms after substantial model changes

Routine model updates usually call for running the existing evaluations with the current
configuration. A substantial model change is also a reason to plan a separate experiment:
does an added prompt rule, context-processing step, or model-based check still improve
assistance? This is a deliberate review, not a requirement after every small revision.

First evaluate the new model with the existing configuration. Then disable one mechanism
in a test configuration and compare the same cases, starting states, and grading rules.
Use judges checked against human judgments. Include cases where the mechanism should
prevent a mistake and cases where it might unnecessarily refuse, delay, or complicate a
valid request. Review task completion and the person's effort as well as scores, response
time, and model usage.

Keep the candidate configuration unchanged while checking it with held-out cases. Remove
the mechanism only when the evidence supports doing so; if the result is uncertain, keep
it and record what remains unknown. Preserve the earlier configuration so it can be restored.
Declarations and explicit test settings make these comparisons possible without rewriting
the application for each experiment. The Todo sample's
[guard selection settings](../guides/models.md#guards) illustrate this for declared guards.

Keep application-enforced permissions, required approvals, validation, and audit records
in place during these experiments. Those controls implement product requirements; better
model behavior does not replace them. The
[model-update procedure](../guides/evaluation-results.md#when-the-provider-changes-the-model)
covers routine checks for regressions.

## Check that a fix generalizes

Create a separate case for the same job with different data and wording. Keep it out of the development session, and run it after development of the fix is complete. Keep its contents and detailed results outside the development process. Once that evidence is used to diagnose or improve the system, move it into the visible set and replace it with a fresh held-out case. Running a held-out case without reading its contents or results does not use it up. Review tool descriptions for phrases copied from failing examples; the tool should describe a class of jobs.

A useful report lets a reviewer move from a run's totals to the request, the state after each turn, the tool results and the grader's reason. Neither a large score table nor a trace without application state supplies that context.

Next, [run the evaluations and read evidence and variation](../guides/evaluation-results.md). [Optional tracing](../guides/langfuse.md) supplements the local reports; it does not own the cases or grading rules.
