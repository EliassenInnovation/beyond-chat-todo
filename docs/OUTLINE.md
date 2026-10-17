# Guide structure

The README introduces the purpose and minimum setup. The guide combines the principles,
working implementation and evaluation method into one sequence. The original standalone
principles and evaluation bodies are no longer maintained; their old URLs point readers here.

| Part | Chapters and reader's questions |
| --- | --- |
| Design | Why an embedded agent? Shared capabilities and the registry; understanding requests and follow-ups; authority and recovery; tools and current evidence; interfaces and views. |
| Implementation | Run the sample, follow a request through shared execution, and choose models for the different roles. |
| Evaluation | Explore with people and personas; define outcomes and calibrate judges; run evaluations and interpret complete evidence and variation; add optional tracing. |
| Application | Choose one useful job in an existing product, preserve its behavior, share its operation, and measure the benefit. |
| Review references | Stable implementation checks, the sample's coverage and limitations, and sources supporting the guidance. |

Use diagrams beside the concept they explain. Keep headings and captions in Markdown,
retain the diagram's relationships, and size labels for the reading column. No slide titles
or decorative chevrons. Screenshots illustrate interactions, not reliability claims.

The guide lives at `guide/` on GitHub Pages; the recorded evaluation report stays at the root.
Build and link-check the same Markdown sources used for reading on GitHub. Git preserves
superseded text; do not add revision histories or abandoned experiment narratives to the guide.

## Reader progression

Introduce the user's problem before the mechanism. Connect new concepts to familiar UI,
service-layer, API and testing practices, and define new terms when first needed. Use one
concrete example through explanation, evidence and action; the appointment example explains
the architecture and the todo sample makes the code inspectable.

Use **Consider** callouts for application-specific decisions and **Practice** callouts for
small artifacts: write a job description, sketch an operation, predict an outcome or inspect
a recorded interaction. Prompts are optional and should build on the reader's own example.
Avoid a box in every section, decorative diagrams, and quizzes that test vocabulary alone.
The reader should leave with a scoped implementation brief. This adapts Bowman's
[4Cs map](https://bowperson.com/images/resources/quick-guide-to-four-c-map.pdf) to a guide.
