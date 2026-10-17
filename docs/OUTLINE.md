# Guide outline and material map

This is the editorial plan for one continuous guide. The README provides the invitation and
minimum setup; the guide explains the decisions, demonstrates them, and helps readers adapt them.
Existing chapter files remain the canonical sources rather than being copied into a second book.

| Chapter | Reader's question and coverage | Material and visual treatment |
| --- | --- | --- |
| Start here | What is this guide, who is it for, and what will I build? | New introduction; plain language, no unexplained check numbers. |
| 1. Why put an agent in the app? | Where does assistance earn its keep? How does it differ from help search? | October 13 motivation and two-languages explanation; wagon, laptop, assistance ladder and two-language diagram. |
| 2. Design the connection | How do shared capabilities, caller authority, context, guards, receipts and recovery fit together? | New connecting narrative drawn from the principles and talk; shared-capability and screen-state diagrams. Distinguish recommendations from this sample's guarantees. |
| 3. Run the sample | What do I install, which key do I need, what can I try without a model? | Setup from README, two provider choices, first three interactions; no secrets. |
| 4. Follow a request | Where does a UI event or tool call go? What happens on ambiguity, approval, failure or recovery? | Existing walkthrough integrated as the central implementation chapter; architecture and screen diagrams alongside code links. |
| 5. Choose models | Which roles need models? What are structured responses and decision models? How do I compare cost and quality? | Existing models guide, including tested configurations and limitations; distinguish model selection from permission. |
| 6. Explore the experience | How do people and personas find new problems? What does visible vs headless testing establish? | Extract runner instructions from README; screenshots, sampling and structured persona turn; retain one canonical explanation in walkthrough. |
| 7. Evaluate outcomes | What constitutes success? How do I check a judge and avoid tuning to test wording? | Existing evaluation method; adapted improvement-loop diagram and chapter introduction. |
| 8. Read evidence and variation | Is evidence complete, is behavior changing, is it acceptable? What changes invalidate limits? | Existing results guide; report screenshot, fixed baseline and comparison periods, practical run commands. |
| 9. Trace when useful | How does this sample connect to Langfuse? What stays local? | Existing short optional integration; no container tutorial or vendor endorsement. |
| 10. Apply it to your application | How do I start with one useful job and improve the capability rather than patch one prompt? | New practical handoff chapter; production gaps and example scope. |
| Reference: design principles | What is the fuller rationale and provenance? | Existing principles, kept as reference rather than required introductory reading. |
| Reference: acceptance checks | How do I inspect a scoped implementation? | Existing implementation guide and checks, preserving their identifiers. |
| Reference: sample assessment | What does this sample demonstrate, and what does it not? | Existing assessment; no suggestion that it meets every check. |

## Diagram decisions

Reuse the talk's diagram bodies as editable SVGs: two languages, shared capabilities,
screen observation/control, and evaluation improvement loop. Remove slide titles, subtitles,
chevrons and unused canvas. Keep generous whitespace around the diagram and put headings and
explanations in Markdown. Retain internal labels because they identify the parts of the diagram.
The existing ladder has already been adapted for documents. Avoid the old approval and eval
slides where their wording would overstate current guarantees. Screenshots are examples of
individual interactions, not reliability evidence. No decorative slide wrappers or embedded page titles.

## Publishing and maintenance

The guide lives at `guide/` on the existing Pages site; the evaluation report stays at the root.
Markdown remains readable on GitHub. Build from the same chapter files, with navigation,
search, chapter links and responsive layouts. Keep configuration and run records authoritative:
no paid runs or application behavior changes are needed for this documentation work.
