# Run the sample


Python 3.11 or later is required.

```bash
./setup.sh
.venv/bin/python -m streamlit run todo/app.py --server.address 127.0.0.1
```

Setup installs the dependencies and creates `.env` from `.env.example` if absent. It does
not edit shell profiles or access a credential vault. The list works without API keys.
For chat and paid evaluations, choose `EVALBASICS_PROVIDER=openai` or `anthropic` in `.env`
and supply that provider's API key. The profile selects models for all roles; only one key is needed.
Conversation and list data are sent to the model provider when you use chat. The example
configuration enables intent and action guards for completion, dates, deletion requests,
and unnamed merges. The OpenAI profile uses the Decisions API for its merge guard. The Anthropic profile
uses boolean judgments for all guards; neither changes the code-enforced approval rules. Existing installations should copy the
`EVALBASICS_GUARDS` selection from `.env.example` if they already specify a smaller set.
See the model guide for configuration and provider compatibility.

Langfuse is optional. Configure this project's own keys if you want synthetic evaluation
or persona traces; no credentials are borrowed from other repositories. Ordinary app chats
are not exported to Langfuse.

For model selection, provider compatibility, credentials and comparison runs, see
[Bring your own model](../guides/models.md).

For this app’s optional tracing setup, see [Langfuse integration](../guides/langfuse.md).
For evidence completeness, run history, control limits, and acceptance criteria, see
[reading evaluation results](../guides/evaluation-results.md).


## Try three different requests

Use a scratch list with synthetic tasks. Ask “How do I hide completed tasks?”, then
“Show me where”, then “Do it.” Compare the reply with what the screen does: instructions,
a highlighted control, and a changed filter are different outcomes.

No API key is needed to inspect the shared operations:

```bash
python3 -m todo.walkthrough
```

This uses disposable data and checks real application behavior without calling a model.
Continue with [the implementation walkthrough](../guides/walkthrough.md).
