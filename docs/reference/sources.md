# Sources and further reading

Chapters link directly to sources beside the passages they support, using the author or
organization and a short title. This bibliography keeps the full details and notes about
each source's relevance and limits. Source review dates are noted where available; these references support the guidance
rather than establish current provider compatibility.

- **Alistair Cockburn (2005).** [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture). Driving the same application through user interfaces, programs, and tests. The central capability catalog here is an application of that separation, not a requirement of the original pattern.

- **Martin Fowler (2006).** [GUI Architectures](https://martinfowler.com/eaaDev/uiArchs.html). Separating presentation from domain logic and synchronizing views through events. It does not prescribe the agent-feedback contract proposed here.

- **Eric Horvitz (1999).** [Principles of Mixed-Initiative User Interfaces](https://www.microsoft.com/en-us/research/publication/principles-mixed-initiative-user-interfaces/). Combining direct manipulation with automated assistance. The idea predates today's language models.

- **Jakob Nielsen (1994; updated 2024).** [10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics/). Visible status, user control and undo, consistency, and actionable errors.

- **Saleema Amershi and colleagues (2019).** [Guidelines for Human-AI Interaction](https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/). Understand and complete the request; Tools and current evidence. Context-sensitive assistance, communicating limitations, and supporting correction.

- **W3C.** [Understanding WCAG 2.1: Status Messages (4.1.3)](https://www.w3.org/WAI/WCAG21/Understanding/status-messages.html). Making status available without moving focus; applied here as an interaction idea beyond the web.

- **Jerome Saltzer and Michael Schroeder (1975).** [The Protection of Information in Computer Systems: Basic Principles](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html). Least privilege, safe defaults, and checking authority on every access. Their security meaning of "capability" differs from this document's application operation.

- **OWASP.** [LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html). Indirect injection and defenses at tool boundaries. Prompt labels alone are not enforcement.

- **Shunyu Yao and colleagues (ICLR 2023).** [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629). Interleaving reasoning, actions, and external observations; precedent for reading through tools.

- **Shunyu Yao and colleagues (2024).** [τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/abs/2406.12045). Simulated users, database-state checks, and repeated trials. It does not validate personas as a replacement for customer research.

- **Lianmin Zheng and colleagues (2023).** [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685). Comparing model judges with human judgments, and their biases. Agreement in one study does not establish accuracy in another application.

- **OpenAI.** [Function-calling best practices](https://developers.openai.com/api/docs/guides/function-calling#best-practices-for-defining-functions). Clear names, schemas that prevent invalid combinations, and moving predictable work to code. Checked September 13, 2026.

- **OpenTelemetry.** [Handling sensitive data](https://opentelemetry.io/docs/security/handling-sensitive-data/). Implementation guide. Data minimization in observability infrastructure. Consulted September 18, 2026.

- **Langfuse.** [Access control](https://langfuse.com/docs/administration/rbac) and [Managing personal data](https://langfuse.com/security/manage-personal-data). Implementation guide. Examples of access, masking, and retention controls to evaluate for a deployment; not a requirement to adopt this vendor. Consulted September 18, 2026.

- **Jianpeng Cheng and colleagues (2020).** [Conversational Semantic Parsing for Dialog State Tracking](https://aclanthology.org/2020.emnlp-main.651/). Structured representations of goals, parameters, and coreference. Consulted September 20, 2026.

- **Jacob Andreas and colleagues (2020).** [Task-Oriented Dialogue as Dataflow Synthesis](https://aclanthology.org/2020.tacl-1.36/). Explicit reference and revision across turns; a research architecture, not a requirement. Consulted September 20, 2026.

- **Vevake Balaraman and colleagues (2023).** [No that's not what I meant: Handling Third Position Repair in Conversational Question Answering](https://aclanthology.org/2023.sigdial-1.52/). Understand and complete the request, and Check 2.7. User corrections after an erroneous assistant response. Consulted September 20, 2026.

- **Model Context Protocol.** [Specification 2026-07-28: Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools), including tool annotations. Authority and recovery, and the implementation checks. Annotations are hints; clients must treat them as untrusted unless they come from trusted servers. Consulted October 3, 2026.

- **Anthropic (January 9, 2026).** [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). Further reading on evaluation. pass@k and pass^k, and how they diverge as the number of trials grows. Consulted October 3, 2026.

- **Bowen Ye and colleagues (2026).** [Claw-Eval: Towards Trustworthy Evaluation of Autonomous Agents](https://arxiv.org/abs/2604.06132). Further reading on evaluation. Pass@3 and Pass^3 under injected service errors across 14 models. One benchmark's result, not a general rate. Consulted October 3, 2026.

- **OpenTelemetry.** [GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai). Implementation guide. Agent spans, MCP spans, and the `gen_ai.evaluation.result` event; status Development, with no release as of October 3, 2026. Consulted October 3, 2026.

- **AG-UI.** [State management](https://docs.ag-ui.com/concepts/state). Implementation guide. A state object both the agent and the frontend can read and modify, synchronized by snapshot and delta events. Consulted October 3, 2026.

- **Lingjiao Chen and colleagues (2024).** [Are More LLM Calls All You Need? Towards Scaling Laws of Compound Inference Systems](https://arxiv.org/abs/2403.02419). Further reading on evaluation. Majority voting over repeated calls improves easy questions and hurts hard ones. Studied on answering questions, not on judging. Consulted October 3, 2026.

- **Pat Verga and colleagues (2024).** [Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models](https://arxiv.org/abs/2404.18796). Further reading on evaluation. A panel of smaller judges from different model families outperformed a single large judge, with less bias toward its own family. Consulted October 3, 2026.

- **Elliot Kim and colleagues (2025).** [Correlated Errors in Large Language Models](https://arxiv.org/abs/2506.07962). Further reading on evaluation. Errors are substantially correlated across more than 350 models, including models from different providers, with effects on judging. Consulted October 3, 2026.

- **Donald J. Wheeler (1993).** *Understanding Variation: The Key to Managing Chaos.* SPC Press. Common-cause and special-cause variation, process behavior charts, and why reacting to common-cause variation makes results worse. Consulted October 3, 2026.

- **Jim Kalbach (2020).** [The Jobs To Be Done Playbook](https://rosenfeldmedia.com/books/jobs-to-be-done-book/). Rosenfeld Media. A practical introduction to customer needs, desired outcomes, and levels of jobs. The guide's washing-machine and replacement-part examples apply this perspective; they are not quoted from the book.

- **Anthropic (December 19, 2024).** [Building Effective AI Agents](https://www.anthropic.com/engineering/building-effective-agents). "While building our agent for SWE-bench, we actually spent more time optimizing our tools than the overall prompt." Consulted October 4, 2026.

- **Thierry Blankenstein and colleagues (2025).** [BiasBusters: Uncovering and Mitigating Tool Selection Bias in Large Language Models](https://arxiv.org/abs/2510.00307). Models prefer tools that appear earlier in the prompt, and rely more on position when no tool clearly fits best. Consulted October 4, 2026.

- **Anthropic (September 11, 2025).** [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents). Too many tools, or tools that overlap, distract agents; small changes to tool descriptions can produce large improvements. The report also describes using Claude Code and evaluation transcripts to improve tools, with held-out testing. Consulted October 4 and October 25, 2026.

- **Haodong Wen and colleagues (2026).** [Frontier Language Models Struggle to Copy](https://arxiv.org/abs/2607.16072). Current models sometimes fail to copy an input string exactly, even one well within their context window. Consulted October 4, 2026.

- **Karen Kent and Murugiah Souppaya, NIST (September 2006).** [Guide to Computer Security Log Management (SP 800-92)](https://csrc.nist.gov/pubs/sp/800/92/final). Logs "need to be protected from breaches of their confidentiality and integrity"; keeping the original logs unaltered "supports their use for evidentiary purposes." A revision (SP 800-92 Rev. 1) was still a draft when consulted. Consulted October 10, 2026.

- **OWASP.** [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html). Lists the events to record and says to "build in tamper detection so you know if a record has been modified or deleted." Consulted October 10, 2026.

- **Apple.** [Human Interface Guidelines: Undo and redo](https://developer.apple.com/design/human-interface-guidelines/undo-and-redo). "Help people predict the results of undo and redo"; menu items can name the result, "like Undo Typing or Redo Bold." Consulted October 10, 2026.

- **Atul Prakash and Michael J. Knister (1994).** [A Framework for Undoing Actions in Collaborative Systems](https://doi.org/10.1145/198425.198427). ACM Transactions on Computer-Human Interaction 1(4). A framework that "allows users to individually reverse their own changes" when several people edit the same data. Consulted October 10, 2026.

## The agent's place in the interface

The [interface chapter](../guide/agent-experience.md) draws on Amershi and colleagues'
guidelines and the sources below. It cites them beside the guidance they
support. These additional sources were consulted October 18, 2026.

- **SAP.** [Joule panel](https://www.sap.com/design-system/fiori-design-android/v25-4/joule/components/joule-panel). Panel sizes, resizing, minimization, and access to the underlying application.
- **Nielsen Norman Group.** [10 Guidelines for Designing Your Site's AI Chatbots](https://www.nngroup.com/articles/ai-chatbots-design-guidelines/). Relevant suggestions and visible awareness of the user's context.

## Evaluation-driven improvement

The [evaluation chapter](../guide/evaluation.md#let-a-coding-agent-run-budgeted-experiments)
uses these sources for automated improvement and the limits of its scoring. Consulted
October 25, 2026.

- **Lakshya A. Agrawal and colleagues (ICLR 2026).** [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457). Prompt optimization through reflection on execution traces and evaluation feedback.
- **Mohamed Hesham Elganayni and colleagues (2026).** [Exploiting LLM-as-a-Judge Disposition on Free Text Legal QA via Prompt Optimization](https://arxiv.org/abs/2604.20726). Studies how the optimization judge affects transfer to other judges, including judge-specific overfitting.
