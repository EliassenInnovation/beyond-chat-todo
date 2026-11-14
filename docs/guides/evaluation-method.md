# Judges, test cases and experiments

This page holds the detailed method behind [Evaluate outcomes](../guide/evaluation.md).
Read it when you choose a judge, design the set of test cases, or run experiments on
prompts, tools and added checks. [Review results and understand variation](evaluation-results.md)
covers repeated runs, baselines and control charts.

## Choose and check the judges

**Grade quality against the user's goal.** When a judge grades quality, it looks at relevance, specificity, permitted next steps, tone, and coherence against what the user wanted and knew. Require examples and reasons, so a person reading a score can find the turn in the conversation that caused it.

**Code combines the verdicts.** Code merges every verdict into one report and writes any feedback to the agent from a template, so the feedback the agent receives is fixed text that people have read and tested, rather than wording a judge chose. A wrong verdict can still choose the wrong template, which is one reason the judges themselves are checked against people.

**Ask a judge more than once only when its mistakes vary.** Asking the same judge several times and taking the majority answer reduces mistakes that change from one attempt to the next. It does not fix mistakes the judge makes every time; in studies of models answering questions, more votes made hard questions worse, because the wrong answer became more consistent. [Chen et al.: repeated model calls](https://arxiv.org/abs/2403.02419) So ask a judge several times and take the majority answer only when checking it against people shows its mistakes vary between attempts.

**Reduce repeated mistakes by changing the judge or its input.** Judges that compare two answers tend to favor whichever is shown first; for those, ask twice with the order swapped. [Zheng et al.: LLM-as-a-judge](https://arxiv.org/abs/2306.05685) For other repeated mistakes, judges from different model families help, [Verga et al.: judges and juries](https://arxiv.org/abs/2404.18796) though different models often share mistakes, including when they act as judges, [Kim et al.: correlated errors](https://arxiv.org/abs/2506.07962) so checking judges against people is still needed.

**Measure before choosing a judge model.** A narrow judge checks one failure type, such as
claiming a save that did not happen; a broader outcome judge can find omissions beyond
those checks. Compare candidates and combinations against human-reviewed examples of
acceptable and unacceptable answers, requiring evidence for each verdict. State whether
people labeled every example or reviewed a sample of model labels. Inspect false failures
and missed failures, and reserve separate examples for evaluating a changed judge. Compare
cost, response time, unavailable responses, and disagreement patterns alongside accuracy.

## Report consistency and find the cause of variation

**Report whether every attempt succeeds, where consistency matters.** A pass rate says how often one attempt succeeds. But a user who does the same job every week cares whether it works every time. pass^k measures that: whether all k attempts at the same job succeed. [Yao et al.: τ-bench](https://arxiv.org/abs/2406.12045) [Anthropic: demystifying agent evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) For jobs where consistency matters, report it beside the pass rate, and say what k was.

To calculate it, make n attempts at each job, k or more, and count the c that succeed; for that job, pass^k is the number of ways to choose k attempts from the c successes divided by the number of ways to choose k from all n, and the suite's pass^k is the average over its jobs.

**When variation itself is the problem, find its cause.** Sometimes the variation is the problem: a test case that passes about half the time, or an answer that is difficult to classify under the grading rule. More runs will not settle this. Find where the variation comes from before changing anything: the application may be unreliable at this job, the test environment may differ between runs, or the grader may disagree with itself. Fix the application when it is the source, and change the test case or the rule only when they are.

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
Stop changing the fix before you run the [held-out cases](../guide/evaluation.md#check-that-a-fix-generalizes).
The [Todo walkthrough](walkthrough.md) explains how to run its visible and held-out
cases; [Check 6.9](../principles/implementation.md#check-6-9) applies the same separation to
automated optimization. Have someone outside the fixing session prepare the held-out cases.

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
[guard selection settings](models.md#guards) illustrate this for declared guards.

Keep application-enforced permissions, required approvals, validation, and audit records
in place during these experiments. Those controls implement product requirements; better
model behavior does not replace them. The
[model-update procedure](evaluation-results.md#when-the-provider-changes-the-model)
covers routine checks for regressions.
