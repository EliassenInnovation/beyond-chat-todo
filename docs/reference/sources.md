# Sources and further reading


Chapters link directly to sources beside the passages they support, using the author or
organization and a short title. This bibliography keeps the full details and notes about
each source's relevance and limits. The numbered entries remain stable for earlier references. Source review dates are noted where available; these references support the guidance rather than establish current provider compatibility.

1. **Alistair Cockburn (2005).** [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture). Driving the same application through user interfaces, programs, and tests. The central capability catalog here is an application of that separation, not a requirement of the original pattern.

2. **Martin Fowler (2006).** [GUI Architectures](https://martinfowler.com/eaaDev/uiArchs.html). Separating presentation from domain logic and synchronizing views through events. It does not prescribe the agent-feedback contract proposed here.

3. **Eric Horvitz (1999).** [Principles of Mixed-Initiative User Interfaces](https://www.microsoft.com/en-us/research/publication/principles-mixed-initiative-user-interfaces/). Combining direct manipulation with automated assistance. The idea predates today's language models.

4. **Jakob Nielsen (1994; updated 2024).** [10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics/). Visible status, user control and undo, consistency, and actionable errors.

5. **Saleema Amershi and colleagues (2019).** [Guidelines for Human-AI Interaction](https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/). Sections 2 and 4. Context-sensitive assistance, communicating limitations, and supporting correction.

6. **W3C.** [Understanding WCAG 2.1: Status Messages (4.1.3)](https://www.w3.org/WAI/WCAG21/Understanding/status-messages.html). Making status available without moving focus; applied here as an interaction idea beyond the web.

7. **Jerome Saltzer and Michael Schroeder (1975).** [The Protection of Information in Computer Systems: Basic Principles](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html). Least privilege, safe defaults, and checking authority on every access. Their security meaning of "capability" differs from this document's application operation.

8. **OWASP.** [LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html). Indirect injection and defenses at tool boundaries. Prompt labels alone are not enforcement.

9. **Shunyu Yao and colleagues (ICLR 2023).** [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629). Interleaving reasoning, actions, and external observations; precedent for reading through tools.

10. **Shunyu Yao and colleagues (2024).** [τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/abs/2406.12045). Simulated users, database-state checks, and repeated trials. It does not validate personas as a replacement for customer research.

11. **Lianmin Zheng and colleagues (2023).** [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685). Comparing model judges with human judgments, and their biases. Agreement in one study does not establish accuracy in another application.

12. **Martin Fowler (2004; revised 2024).** [Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html). Incremental modernization while an existing system keeps running.

13. **OpenAI.** [Define tools](https://developers.openai.com/plugins/plan/tools). Starting from user outcomes, grouping coherent actions, and separating reads from writes. Checked September 13, 2026.

14. **OpenAI.** [Function-calling best practices](https://developers.openai.com/api/docs/guides/function-calling#best-practices-for-defining-functions). Clear names, schemas that prevent invalid combinations, and moving predictable work to code. Checked September 13, 2026.

15. **OpenTelemetry.** [Handling sensitive data](https://opentelemetry.io/docs/security/handling-sensitive-data/). Implementation guide. Data minimization in observability infrastructure. Consulted September 18, 2026.

16. **Langfuse.** [Access control](https://langfuse.com/docs/administration/rbac) and [Managing personal data](https://langfuse.com/security/manage-personal-data). Implementation guide. Examples of access, masking, and retention controls to evaluate for a deployment; not a requirement to adopt this vendor. Consulted September 18, 2026.

17. **Jianpeng Cheng and colleagues (2020).** [Conversational Semantic Parsing for Dialog State Tracking](https://aclanthology.org/2020.emnlp-main.651/). Structured representations of goals, parameters, and coreference. Consulted September 20, 2026.

18. **Jacob Andreas and colleagues (2020).** [Task-Oriented Dialogue as Dataflow Synthesis](https://aclanthology.org/2020.tacl-1.36/). Explicit reference and revision across turns; a research architecture, not a requirement. Consulted September 20, 2026.

19. **Vevake Balaraman and colleagues (2023).** [No that's not what I meant: Handling Third Position Repair in Conversational Question Answering](https://aclanthology.org/2023.sigdial-1.52/). Section 2 and Check 2.7. User corrections after an erroneous assistant response. Consulted September 20, 2026.

20. **Model Context Protocol.** [Specification 2026-07-28: Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools), including tool annotations. Section 3 and implementation guide. Annotations are hints; clients must treat them as untrusted unless they come from trusted servers. Consulted October 3, 2026.

21. **Anthropic (January 9, 2026).** [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). Further reading on evaluation. pass@k and pass^k, and how they diverge as the number of trials grows. Consulted October 3, 2026.

22. **Bowen Ye and colleagues (2026).** [Claw-Eval: Towards Trustworthy Evaluation of Autonomous Agents](https://arxiv.org/abs/2604.06132). Further reading on evaluation. Pass@3 and Pass^3 under injected service errors across 14 models. One benchmark's result, not a general rate. Consulted October 3, 2026.

23. **OpenTelemetry.** [GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai). Implementation guide. Agent spans, MCP spans, and the `gen_ai.evaluation.result` event; status Development, with no release as of October 3, 2026. Consulted October 3, 2026.

24. **AG-UI.** [State management](https://docs.ag-ui.com/concepts/state). Implementation guide. A state object both the agent and the frontend can read and modify, synchronized by snapshot and delta events. Consulted October 3, 2026.

25. **Hamel Husain (March 24, 2025).** [A Field Guide to Rapidly Improving AI Products](https://hamel.dev/blog/posts/field-guide/). A customized data viewer that shows all the context in one place, described as the most impactful investment AI teams make. Consulted October 3, 2026.

26. **Hamel Husain and Shreya Shankar (updated September 18, 2026).** [AI Evals: Everything You Need to Know](https://hamel.dev/blog/posts/evals-faq/). Building a custom annotation tool rather than using an off-the-shelf one, except for large distributed annotation teams. Consulted October 3, 2026.

27. **Lingjiao Chen and colleagues (2024).** [Are More LLM Calls All You Need? Towards Scaling Laws of Compound Inference Systems](https://arxiv.org/abs/2403.02419). Further reading on evaluation. Majority voting over repeated calls improves easy questions and hurts hard ones. Studied on answering questions, not on judging. Consulted October 3, 2026.

28. **Pat Verga and colleagues (2024).** [Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models](https://arxiv.org/abs/2404.18796). Further reading on evaluation. A panel of smaller judges from different model families outperformed a single large judge, with less bias toward its own family, at over seven times lower cost. Consulted October 3, 2026.

29. **Elliot Kim and colleagues (2025).** [Correlated Errors in Large Language Models](https://arxiv.org/abs/2506.07962). Further reading on evaluation. Errors are substantially correlated across more than 350 models, including models from different providers, with effects on judging. Consulted October 3, 2026.

30. **Donald J. Wheeler (1993).** *Understanding Variation: The Key to Managing Chaos.* SPC Press. Common-cause and special-cause variation, process behavior charts, and why reacting to common-cause variation makes results worse. Consulted October 3, 2026.

31. **Jim Kalbach (2020).** [The Jobs To Be Done Playbook](https://rosenfeldmedia.com/books/jobs-to-be-done-book/). Rosenfeld Media. A practical introduction to customer needs, desired outcomes, and levels of jobs. The guide's appointment example applies this perspective; it is not quoted from the book.

32. **Anthropic (December 19, 2024).** [Building Effective AI Agents](https://www.anthropic.com/engineering/building-effective-agents). "While building our agent for SWE-bench, we actually spent more time optimizing our tools than the overall prompt." Consulted October 4, 2026.

33. **Thierry Blankenstein and colleagues (2025).** [BiasBusters: Uncovering and Mitigating Tool Selection Bias in Large Language Models](https://arxiv.org/abs/2510.00307). Models prefer tools that appear earlier in the prompt, and rely more on position when no tool clearly fits best. Consulted October 4, 2026.

34. **Anthropic (September 11, 2025).** [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents). Too many tools, or tools that overlap, distract agents; small changes to tool descriptions can produce large improvements. Consulted October 4, 2026.

35. **Haodong Wen and colleagues (2026).** [Frontier Language Models Struggle to Copy](https://arxiv.org/abs/2607.16072). Current models sometimes fail to copy an input string exactly, even one well within their context window. Consulted October 4, 2026.

36. **Google Cloud.** [Introduction to function calling](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling). A generic, low-level tool may be used more often but less accurately; a specific, high-level tool is used more accurately but less often. Consulted October 4, 2026.

37. **Jason Lemkin (July 2025).** [Post on X about Replit's agent deleting a production database](https://x.com/jasonlk/status/1946069562723897802). The founder's own account, posted July 18, 2025: an agent deleted his company's production database during a code freeze. Replit's rollback, which the agent had said would not work, recovered the data, and Replit's chief executive then announced automatic separation of development and production databases ([The Register, July 22, 2025](https://www.theregister.com/2025/07/22/replit_saastr_response/)). Consulted October 4, 2026.

38. **OpenAI.** [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs). Announced August 6, 2024 ([announcement](https://openai.com/index/introducing-structured-outputs-in-the-api/)); "ensures the model will always generate responses that adhere to your supplied JSON Schema." Refusals and replies cut off at the token limit are reported separately. Consulted October 4, 2026.

39. **Anthropic.** [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs). Generally available on the Claude API since January 29, 2026 ([release notes](https://platform.claude.com/docs/en/release-notes/overview)); "guarantee schema-compliant responses through constrained decoding," with exceptions for refusals and replies cut off at the token limit. Consulted October 4, 2026.

40. **Google.** [Structured output](https://ai.google.dev/gemini-api/docs/structured-output?hl=en) (Gemini API). Responses "adhere to a provided JSON Schema"; the documentation advises to "always validate values in your application." Consulted October 4, 2026.

41. **Beatrice Nolan, Fortune (July 23, 2025).** [An AI-powered coding tool wiped out a software company's database, then apologized for a "catastrophic failure on my part"](https://fortune.com/2025/07/23/ai-coding-tool-replit-wiped-database-called-it-a-catastrophic-failure/). Reports that the incident "occurred despite the system being in a designated 'code and action freeze'" and wiped data for more than 1,200 executives. Consulted October 4, 2026.

42. **Karen Kent and Murugiah Souppaya, NIST (September 2006).** [Guide to Computer Security Log Management (SP 800-92)](https://csrc.nist.gov/pubs/sp/800/92/final). Logs "need to be protected from breaches of their confidentiality and integrity"; keeping the original logs unaltered "supports their use for evidentiary purposes." A revision (SP 800-92 Rev. 1) was still a draft when consulted. Consulted October 10, 2026.

43. **OWASP.** [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html). Lists the events to record and says to "build in tamper detection so you know if a record has been modified or deleted." Consulted October 10, 2026.

44. **U.S. Securities and Exchange Commission (October 12, 2022).** [Electronic Recordkeeping Requirements for Broker-Dealers (Release 34-96034)](https://www.sec.gov/rules/final/2022/34-96034.pdf). Adds an audit-trail alternative to write-once storage: records are kept so that an original can be recreated if it is modified or deleted, with the time of each action and who took it. It governs broker-dealer records; we cite it for the principle, not as a requirement on other applications. Consulted October 10, 2026.

45. **FINRA (December 9, 2025).** [2026 Annual Regulatory Oversight Report: GenAI](https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report/gen-ai). Describes firms logging prompts and outputs for accountability and troubleshooting and tracking model versions, and lists how to track an AI agent's actions and decisions as a supervision question. Consulted October 10, 2026.

46. **Apple.** [Human Interface Guidelines: Undo and redo](https://developer.apple.com/design/human-interface-guidelines/undo-and-redo). "Help people predict the results of undo and redo"; menu items can name the result, "like Undo Typing or Redo Bold." Consulted October 10, 2026.

47. **Atul Prakash and Michael J. Knister (1994).** [A Framework for Undoing Actions in Collaborative Systems](https://doi.org/10.1145/198425.198427). ACM Transactions on Computer-Human Interaction 1(4). A framework that "allows users to individually reverse their own changes" when several people edit the same data. Consulted October 10, 2026.

48. **Sharon L. Bowman.** [A Quick Guide to the 4Cs Map](https://bowperson.com/images/resources/quick-guide-to-four-c-map.pdf), accompanying *Training from the Back of the Room!*. Connections, concepts, concrete practice and conclusions inform this guide's reader prompts. This is an adaptation for self-directed documentation, not a claim that the guide implements a facilitated training course.


## The agent's place in the interface

The [interface chapter](../guide/agent-experience.md) draws on Amershi and colleagues'
guidelines (entry 5 above) and the sources below. It cites them beside the guidance they
support. These additional sources were consulted October 18, 2026.

- **SAP.** [Joule panel](https://www.sap.com/design-system/fiori-design-android/v25-4/joule/components/joule-panel). Panel sizes, resizing, minimization, and access to the underlying application.
- **Nielsen Norman Group.** [10 Guidelines for Designing Your Site's AI Chatbots](https://www.nngroup.com/articles/ai-chatbots-design-guidelines/). Relevant suggestions and visible awareness of the user's context.


## Evaluation-driven improvement

The [evaluation chapter](../guide/evaluation.md#let-a-coding-agent-run-budgeted-experiments)
uses these sources for automated improvement and the limits of its scoring. Consulted
October 25, 2026.

- **Anthropic (2025).** [Writing effective tools for agents — with agents](https://www.anthropic.com/research/writing-tools-for-agents). Engineering report on using Claude Code and evaluation transcripts to improve tools, with held-out testing.
- **Lakshya A. Agrawal and colleagues (ICLR 2026).** [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457). Prompt optimization through reflection on execution traces and evaluation feedback.
- **Mohamed Hesham Elganayni and colleagues (2026).** [Exploiting LLM-as-a-Judge Disposition on Free Text Legal QA via Prompt Optimization](https://arxiv.org/abs/2604.20726). Studies how the optimization judge affects transfer to other judges, including judge-specific overfitting.
