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
