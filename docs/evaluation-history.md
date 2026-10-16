# Earlier evaluation findings

These historical measurements were recorded during earlier development. They are examples
of the improvement process, not current reliability claims:

| Case | Before | Fix | After |
|---|---|---|---|
| `complete-by-name`: "I went to the dentist" | 0/5: offered to add a reminder | One sentence in the tool's description | 5/5 |
| `read-fresh`: tick a box in the app, then "everything I haven't done is due Friday" | 0/3: dated the finished todo from memory | Code refuses a change until the agent has read the current list | 5/5 |
| `the-plumber-too`: "I called mom", then "and the plumber too" | 20/26: answered without looking at the list | The list now comes with every message (orientation), so the agent never has to decide to look | 30/30 |
| `which-call`: "the call needs to happen Monday" with two calls on the list | 0/5 after adding the `move_todo` tool (5/5 before; removing the tool restores it; see commit 68627f6) | `set_due_date`'s description: ask when the words fit more than one todo | 5/5 |

The prompt already told the agent to read the list first. It did not. A prompt can ask; code
can require. And a new capability can break an old behavior nobody touched: run the whole
suite after every change. The same held for a single prompt sentence: "Assume everything
the user says is about their todo list" took `which-call` from 5/5 to 0/5 (the agent acted on
the first match instead of asking), and attaching "if more than one fits, ask" did not save it.
The list already made the point the sentence was trying to make, so the sentence came out.


For current interpretation, see [reading evaluation results](evaluation-signals.md).
