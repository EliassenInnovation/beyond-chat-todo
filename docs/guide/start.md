# Run the sample

Python 3.11 or later is required. Run the commands from the cloned repository's root folder.
If you want to inspect the shared operations before installing dependencies or supplying a key:

```bash
python3 -m todo.walkthrough
```

It uses disposable data and makes no model calls. For the interactive app:

```bash
./setup.sh
.venv/bin/python -m streamlit run todo/app.py --server.address 127.0.0.1
```

Setup installs the dependencies and creates `.env` from `.env.example` if absent. It does
not edit shell profiles or access a credential vault. The list works without API keys.
For chat and paid evaluations, choose `EVALBASICS_PROVIDER=openai` or `anthropic` in `.env`
and supply that provider's API key. The profile selects models for all roles; only one key is needed.
Conversation and list data are sent to the model provider when you use chat. Guards are enabled by default to check whether proposed changes fit the request.
Keep the defaults for this first run; the [model chapter](../guides/models.md) explains
provider differences and how to update an existing configuration.

Langfuse is optional. Configure this project's own keys if you want synthetic evaluation
or persona traces; no credentials are borrowed from other repositories. Ordinary app chats
are not exported to Langfuse.

For model selection, provider compatibility, credentials and comparison runs, see
[Bring your own model](../guides/models.md).

For this app’s optional tracing setup, see [Langfuse integration](../guides/langfuse.md).
For evidence completeness, run history, control limits, and acceptance criteria, see
[reading evaluation results](../guides/evaluation-results.md).

## Try three different requests

Use a separate test list with synthetic tasks. Ask “How do I hide completed tasks?”, then
“Show me where”, then “Do it.” Compare the reply with what the screen does: instructions,
a highlighted control, and a changed filter are different outcomes.

!!! practice "Practice — predict, then compare"
    Before sending each of the three requests, write down what you expect to change: the
    explanation, the highlighted control, or the visible list. Compare the actual result
    with that prediction. If you have no API key, use the offline walkthrough to inspect
    the operations; it cannot tell you whether a model chooses the right one.

Continue with [the implementation walkthrough](../guides/walkthrough.md).
