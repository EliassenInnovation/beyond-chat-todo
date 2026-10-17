# October 13 deck-to-guide audit

Reviewed the talk track's 44 sections against the guide and checked the deck's `OCT13`
sequence for its associated examples and visuals. This is an editorial record, not another
reader-facing chapter. Source: the original project's `tour/script.md`, `tour/build.py`,
and `tour/oct13-*.svg` / `oct13-api-agent.png`.

**Incorporated** identifies material added during this pass. **Covered** identifies an idea
already explained in the guide. **Presentation-only** records an intentional omission.
Numerical claims from historical experiments are not carried forward as current results.
The registry and API diagrams are adapted without slide headings, subtitles or decoration.

| Talk section | Treatment | Guide destination and reason |
| --- | --- | --- |
| Only a persona's or a tester's chat leaves the app, and the screen says when; a production chat never does. | Covered | [guides/langfuse.md](guides/langfuse.md). Keep the short sample integration; do not copy dated SDK instructions. |
| Three ways to run it: their cloud, one machine, or your Kubernetes. Self-hosting means six parts. | Presentation-only | Container and hosting tutorial omitted by scope. |
| 1. Swap the import: every model call becomes a generation, with tokens, cost and the model that served it. | Covered | [guides/langfuse.md](guides/langfuse.md). Keep the short sample integration; do not copy dated SDK instructions. |
| Evals give you evidence that the agent works. | Covered | [principles/evaluating-agents.md](guide/evaluation.md). Code checks outcomes; calibrated judges inspect language; review both failures and passes. Historical counts are not current evidence. |
| Asked how to merge two todos, then to do it, it picked the bouncy castles itself. | Incorporated | [guides/evaluation-results.md](guides/evaluation-results.md). Concrete distinction between an ambiguous request, action evidence, and grader judgment; do not reuse old failure rates. |
| Before and after: two fixes, and the second came from a person reading a trace of what the app sent the model. | Incorporated | [guides/evaluation-results.md](guides/evaluation-results.md). Concrete distinction between an ambiguous request, action evidence, and grader judgment; do not reuse old failure rates. |
| Your app name goes here. | Covered | [guide/why.md](guide/why.md). Motivation, ladder, two languages and existing images. |
| Friends don't let friends use bad chatbots. | Covered | [guide/why.md](guide/why.md). Motivation, ladder, two languages and existing images. |
| How I got here: from copying and pasting to an agent in the app. | Presentation-only | Personal origin story is useful in the talk, unnecessary to follow the sample. |
| Rungs 1 and 2 point you at help: you still do the work. | Covered | [guide/why.md](guide/why.md). Motivation, ladder, two languages and existing images. |
| Rungs 3 to 5: a partner that tells, shows, and does. | Covered | [guide/why.md](guide/why.md). Motivation, ladder, two languages and existing images. |
| Rung 6: something new, built from the app's parts. | Covered | [guides/walkthrough.md](guides/walkthrough.md). Tell/show/do and composing operations, with explicit reliability limits. |
| People use two languages with the agent. | Covered | [guide/why.md](guide/why.md). Motivation, ladder, two languages and existing images. |
| Understanding the people and the app, and the capabilities built on it. | Covered | [guide/design.md](guide/design.md). Shared capabilities and screen observation/control diagrams. |
| The UI, for people, is built on the capabilities. | Covered | [guide/design.md](guide/design.md). Shared capabilities and screen observation/control diagrams. |
| Capabilities first. The UI and the agent are built on them. | Covered | [guide/design.md](guide/design.md). Shared capabilities and screen observation/control diagrams. |
| The agent sees what you see, and can work the app. | Covered | [guide/design.md](guide/design.md). Shared capabilities and screen observation/control diagrams. |
| Tell me how. Show me. Do it for me. | Covered | [guides/walkthrough.md](guides/walkthrough.md). Tell/show/do and composing operations, with explicit reliability limits. |
| Live, as the Exploratory Tester: clear the done ones, merge two, plan a party; then the session in Langfuse. | Covered | [guide/exploration.md](guide/exploration.md). Visible and headless exploration, human sampling; screenshots replace live stage directions. |
| Can it be undone? How much does it touch? | Incorporated | [guide/design.md](guide/design.md). Registry declaration and annotated example; impact versus recovery; general and job-specific tools; API reuse and extracting screen logic. Includes robot illustration. |
| The capability registry: placing an order, declared once. | Incorporated | [guide/design.md](guide/design.md). Registry declaration and annotated example; impact versus recovery; general and job-specific tools; API reuse and extracting screen logic. Includes robot illustration. |
| Agent-enabled applications take work to provide real value. | Covered | [guide/apply.md](guide/apply.md). Select useful jobs; understand users; fix tools and context as well as prompts; evaluate effort. Old timings and token counts are not current measurements. |
| Why a good agent in the app is worth the effort. | Covered | [guide/why.md](guide/why.md). Motivation, ladder, two languages and existing images. |
| A plain chatbot sends whatever the model writes. This coach looks things up and checks the answer before you see it. | Presentation-only | Advisor-specific pipeline is not the todo implementation. General authority, guard and receipt principles are explained in the guide. |
| A small prompt and well-designed tools. | Covered | [guide/apply.md](guide/apply.md). Select useful jobs; understand users; fix tools and context as well as prompts; evaluate effort. Old timings and token counts are not current measurements. |
| What we'll cover: from one app with an agent to an agent working across apps. | Presentation-only | Talk agenda and download slide replaced by guide navigation and reference introductions. |
| Where this is going. | Covered | [guide/apply.md](guide/apply.md). Select useful jobs; understand users; fix tools and context as well as prompts; evaluate effort. Old timings and token counts are not current measurements. |
| When apps expose their capabilities through MCP, an agent can combine them. | Incorporated | [guide/apply.md](guide/apply.md). Cross-interface and MCP extension boundaries; omit live financial demo and avoid claiming the sample implements MCP. |
| Specific tools for key jobs, general tools for the rest. | Incorporated | [guide/design.md](guide/design.md). Registry declaration and annotated example; impact versus recovery; general and job-specific tools; API reuse and extracting screen logic. Includes robot illustration. |
| What a good agent depends on. | Covered | [guide/apply.md](guide/apply.md). Select useful jobs; understand users; fix tools and context as well as prompts; evaluate effort. Old timings and token counts are not current measurements. |
| Easier when the app is in layers. | Incorporated | [guide/design.md](guide/design.md). Registry declaration and annotated example; impact versus recovery; general and job-specific tools; API reuse and extracting screen logic. Includes robot illustration. |
| The basic building block: making your app's capabilities accessible. | Incorporated | [guide/design.md](guide/design.md). Registry declaration and annotated example; impact versus recovery; general and job-specific tools; API reuse and extracting screen logic. Includes robot illustration. |
| Deciding which surface gets each capability, and how. | Incorporated | [guide/design.md](guide/design.md). Registry declaration and annotated example; impact versus recovery; general and job-specific tools; API reuse and extracting screen logic. Includes robot illustration. |
| Most APIs are shaped like the data, not the job. | Incorporated | [guide/design.md](guide/design.md). Registry declaration and annotated example; impact versus recovery; general and job-specific tools; API reuse and extracting screen logic. Includes robot illustration. |
| The trace of that conversation in Langfuse. | Covered | [guides/langfuse.md](guides/langfuse.md). Keep the short sample integration; do not copy dated SDK instructions. |
| How the eval checks it: code reads the saved list, and a judge reads the reply. | Covered | [principles/evaluating-agents.md](guide/evaluation.md). Code checks outcomes; calibrated judges inspect language; review both failures and passes. Historical counts are not current evidence. |
| Before and after: a merge tool with a guard of its own stopped the guess. | Incorporated | [guides/evaluation-results.md](guides/evaluation-results.md). Concrete distinction between an ambiguous request, action evidence, and grader judgment; do not reuse old failure rates. |
| Live: Claude with the calendar, the investments app, and the news. | Incorporated | [guide/apply.md](guide/apply.md). Cross-interface and MCP extension boundaries; omit live financial demo and avoid claiming the sample implements MCP. |
| Test and tune the judge: compare it with replies whose truth is known. | Covered | [principles/evaluating-agents.md](guide/evaluation.md). Code checks outcomes; calibrated judges inspect language; review both failures and passes. Historical counts are not current evidence. |
| Live: pick a persona (Sam), press Next a few times, then open "This chat in Langfuse". → moves on. | Covered | [guide/exploration.md](guide/exploration.md). Visible and headless exploration, human sampling; screenshots replace live stage directions. |
| Personas in a real app: Linda, 58, cash heavy and cautious. | Presentation-only | Keep the persona method with the todo screenshot; avoid a second application domain and another setup dependency. |
| Personas in a real app: run Linda turn by turn. | Presentation-only | Keep the persona method with the todo screenshot; avoid a second application domain and another setup dependency. |
| Materials to download: four documents and this deck. | Presentation-only | Talk agenda and download slide replaced by guide navigation and reference introductions. |
| The audit log: a record of every change and every reply. | Incorporated | [guide/apply.md](guide/apply.md). Audit records versus traces, refused attempts, reversal evidence, retention and sample limitations. |
