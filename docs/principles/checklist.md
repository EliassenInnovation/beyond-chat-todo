# Beyond Chat — Agent Checklist

Version 3.5-draft · October 15, 2026

> **Note:** Following these practices does not make an application secure. We have tried red teaming and prompt-injection tests, but encryption, transport security, authentication, and other standard security are outside this document's scope. Security for an application with an agent belongs to corporate governance, with policy and controls in place.

First review the full principles and adapt them to the application. Then use the agreed version with a task of limited scope: the capability, the interfaces, the changes allowed, and the check IDs. For example: “Review rescheduling on the screen and the command line against Checks 3.1–3.7; do not change code.” This checklist does not authorize a general rewrite.

Read [the principles](principles.md) for the reasoning and [the implementation guide](implementation.md) for the detailed checks and contracts that apply to the task. Keep this summary in the agent's standing instructions; read the reasoning when it is needed.

## Who owns what

- The capability owns what an operation is: its purpose, actions, inputs, checks on those inputs, what it changes, its limits, the names and meanings of its inputs, and results that later requests can refer to.
- The model and the code that runs the agent: the model works out what the user is referring to and what a correction changes; the code that runs it keeps the user's requests and the tool history. Application code stores inputs and results and recalculates. No separate component to interpret the conversation is needed.
- Shared execution, the code every operation runs through, owns policy, approval, saving, history, undo, and reporting what actually happened.
- Each interface owns how a caller finds and reaches an operation, and how the result is shown. Screen controls, agent tools, and command-line commands are each designed for their caller and share the same behavior underneath; one capability need not be one tool.

A user's job may need several capabilities. The agent combines them; application code owns any steps that must happen in order, or all together, and how to recover when one fails.

## Inspection and records

When the task covers making the application inspectable, give each action an ID that does not change, a versioned description of its inputs, and a statement of what it changes; send every caller through shared execution. Record the tools each caller was actually offered, and link each call, from inside the app or through MCP, to what happened in the application. Use existing tracing tools, with a written mapping of the application's details onto them. Record conversation content only where policy says so; limit who can read the records, and remove protected data before it leaves. Permission to read the records does not include permission to steer or replay. See the implementation guide for the proposed contract and Checks 1.7–1.11.

References to earlier results: capabilities say what their inputs mean and return results that later requests can refer to. To revise a calculation, the request must say which earlier result it builds on (`based_on`) and what changes (`changes`); never assume the most recent result. Never change an original input or result; return the revision under a new ID and describe it in the user's terms. Keep the dated source data by default; refreshing it is a separate, explicit step. Each stored reference has a scope and an expiry, and holding an ID does not grant permission. Prefer adding or removing members of a group to replacing the whole group; a replacement is explicit and reports what it removed. Evaluate the saved state or calculation, the truth of what was said, and whether the job was finished, separately. See the implementation guide for the proposed contract, which the application code must still implement.

## Check index

- **1.1** Shared behavior; **1.2** Shared validation; **1.3** Adapter boundaries; **1.4** Purpose in the tool's description; **1.5** Interfaces fit their callers; **1.6** Screen actions fit the caller; **1.12** Tools for repeated jobs; **1.13** Screen actions run through the application's own state; **1.14** Views supplement a complete text answer.
- **1.7** Inspectable catalog; **1.8** Offered versus executed; **1.9** Records match what happened; **1.10** Portable inspection; **1.11** Protected observation.
- **2.1** Subject and task; **2.2** Context corrections; **2.3** Complete scope; **2.4** Visible outcomes; **2.5** Jobs in ordinary language; **2.6** Additive references; **2.7** Repair after a wrong turn; **2.8** Reference evidence and boundaries; **2.9** Revise a named result without changing the original; **2.10** Familiar forms, documents, and spreadsheets.
- **3.1** Atomic outcomes; **3.2** Recovery; **3.3** Enforced authority; **3.4** Approval applies to this exact change; **3.5** Combined impact; **3.6** Data and resource boundaries; **3.7** Guards; **3.8** Audit record; **3.9** Undo scope; **3.10** Uncertain outcomes; **3.11** Stopping a request.
- **4.1** Relevant reads; **4.2** Current evidence; **4.3** Delivered history; **4.4** Application-written text; **4.5** Whole-suite rerun; **4.6** One current copy.
- **5.1** Credible scenarios; **5.2** Adaptive exploration; **5.3** Preserved failures; **5.4** Actions available to simulated users.
- **6.1** Outcome evidence; **6.2** Judge calibration; **6.3** Comparable runs; **6.4** Tool independence; **6.5** Served model; **6.6** Checks protect outcomes; **6.7** Grade only model-written text; **6.8** Grader assignment; **6.9** Unseen cases for the same kind of task; **6.10** Reliability across attempts; **6.11** Injected failures; **6.12** Wording borrowed from test cases; **6.13** One place to see what happened; **6.14** Release decision; **6.15** Experiment records.
- **7.1** Scoped integration; **7.2** Bounded delivery.

IDs refer to the full checks in the implementation guide, not to separate tests. Do not renumber or reuse them.

## Seven working rules

1. **Look before proposing.** Follow a real request through execution, saving, feedback, and recovery.
2. **Make gaps concrete.** Separate what is built, what is tested, and what is missing; cite the evidence.
3. **Fix the shared owner.** Keep the application's behavior and its rules out of individual interfaces and prompts. Before adding prompt rules or another model to supervise, read what the model was actually sent: the tool descriptions, the tool results, and any data sent with each message. After any change to tools, results, or the prompt, rerun the whole suite; when that is too slow or costly, rerun the cases closest to the change and the whole suite before each release.
4. **Stay within the task.** Report related gaps separately. Do not fix them without permission.
5. **Check the user's experience.** Through the supported interfaces, check that every item was handled, and check the saved state, what the screen shows, failures, and recovery.
6. **Report evidence and limits.** Say what changed, which checks ran, and what is still open. A passing unit test does not prove the whole interaction works.
7. **Keep held-out cases unseen.** Never run or read a held-out case while fixing. Finish the fix, then run the held-out cases; each one run joins the ordinary cases and a fresh one replaces it. Fix the handling for that kind of request instead of the one failing sentence, and never borrow a test case's wording for a tool.

## Report

One row per check and interface: **Check | Interface | Result | Implemented | Tested | Missing**.

Results: Pass, Fail, Not run, or Not applicable with a reason. Include where the code and tests are and what was observed. Say plainly what was not tested, and keep findings outside the task separate.

## Security scope and evidence

Include persona runners, evaluators, local control sockets, stored traces, and live-test modes in the deployment's threat model. Keeping test data separate is not the same as isolating it at the operating-system level. Keep real users' conversations out of test recording unless that is decided explicitly under your data rules, and make any recording visible to the person in the conversation. Report the controls you tested and the risks that remain, without claiming security or compliance guarantees. Each organization must assess its own deployment and obligations; these principles do not replace qualified security, privacy, or legal review.
