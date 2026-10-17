# Working on this sample

Read README.md and docs/guides/walkthrough.md for the architecture and setup.
Application code is in todo/, eval tools and fixtures in evaluations/, and offline tests in tests/.
Run module commands from the repository root; .env, todos.json, and runs/ stay there.
The illustrated guide under docs/guide/ explains the principles and evaluation method.
The acceptance checks remain in docs/principles/implementation.md.

- Preserve shared action ownership through capabilities.execute; keep authority in code.
- Keep guards separate from deterministic permissions and deletion approval.
- Run pytest for implementation changes. Offline tests must not make model calls.
- For behavior changes, use visible eval cases first. Do not inspect or tune against held-out cases.
- Test grader changes against both correct and incorrect replies; preserve original run records.
- Record model/configuration changes as new comparison periods, not continuation of old limits.
- Langfuse is optional. Never copy credentials or personal task data into public examples.
- Keep the starter focused; historical experiments are not part of its runtime.
