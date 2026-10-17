# Understand and complete the request

Design the conversation around what the person wants to accomplish. A job can be broad, such as keeping track of the companies you follow, more specific, such as tracking their annual meetings, or a single operation, such as marking one to-do item done. [31](../reference/sources.md)

## Start with the job

**Start with what the user wants done.** A user of a scheduling app who says "stop booking me on Friday afternoons" should not have to find the settings screen that controls their availability. The agent finds the right capability and makes the change the user is allowed to make. The preference is saved in the user's settings, where the screen shows it and the user can change it later, not written into the application's code or the agent's prompt.

**Use what you already know about users' jobs to decide where to start.** Many organizations already record what users are trying to do. Call centers often track the reason for each call; in financial services, common ones include changing an address, taking a required minimum distribution, or changing a beneficiary. The application may track it too, such as which tasks people start and abandon. That data shows which jobs cost the most to support, which frustrate users, and which come up most often, and so where agent development should start. Where no such data exists, user research may be needed.

**One request may need several capabilities.** "Compare this quarter's bookings with last year's" may mean reading this quarter's appointments, working out the same period last year, and reading its totals. The agent combines the steps, and each capability still applies its own checks and permissions. Asking for an answer does not give the agent permission to change anything along the way, such as the screen's layout or a saved setting.

**Give steps that must happen together one owner in code.** Some jobs need several steps to happen in a fixed order, or all to succeed or none. Moving an appointment means freeing the old time and booking the new one; the user should never end up with both, or with neither. Do not leave that to the model calling two tools in the right order. Write it as one operation in the application's code, which the agent calls once, and which saves, records, and undoes the change as a whole.

**Understand requests in the user's words or the application's.** A user may ask in the language of what they want to do, "I need a regular meeting with the steering committee," or in the language of the application, "create a recurring meeting." Both should work. Read the whole request and the conversation before it, rather than reacting to particular words: "how do I…" can be a request to be shown how, or a request to have it done.

**Act when the request is clear; ask when it is not.** If the request is clear and allowed, do it. Ask when the possible readings would lead to different results that matter. If the agent offered two options and the user says "sure", the agent does not know which one the user means, and should ask.

## Supply current context

**Tell the agent what the user is looking at.** The agent can give more useful help when it knows what the user is looking at on the screen. Send enough to orient it without overwhelming it with detail it does not need: the current view, the selection, unsaved work, and whether the context changed. If the agent needs more detail to give a better result, it can read it through a tool.

**Choose context by measuring its effect.** Start with the current view, selection, unsaved work, and relevant application data. A small application may supply its whole list; a larger one may supply a summary and tools for further reads. Compare representative requests with different amounts of context. More information is useful only when it improves the outcome.

**Send one current copy, and replace it each turn.** When current application data accompanies each message, replace the previous snapshot rather than accumulating conflicting copies. Keep earlier actions and results as history, clearly distinguished from current state. Inspect the actual model request to verify that this is what it receives.

## Interpret follow-up requests

Keep one task in view across the conversation. The same short phrase can add work, correct
an earlier value, or refer to a record already discussed:

| Follow-up | What it changes | What to preserve |
| --- | --- | --- |
| “The other event type too” | Adds to the requested scope | The original event type remains included. |
| “Sorry, 30 days” | Corrects the time interval | The requested measure and selected records remain the same. |
| “Open it so I can fix that” | Requests navigation to a previously identified problem | The record and the field needing attention. |


**Work out what the user is referring to and what they want done.** People rarely repeat a full request. Suppose the agent has just found that a customer's address fails validation, and the user says "open it so I can fix that." "It" is the customer, and "that" is the address problem. Opening the customer's overview gets the first right and loses the second; the useful place to open is the address editor. Keep track of the task the user is working on, not only the record they have selected, and do not make users repeat what is already clear from the conversation.

**Work out what each follow-up changes.** Short follow-ups do different things. "That customer" says who the request is about; "the other event type too" adds to the earlier request; "sorry, 30 days" corrects one detail of it. Keep the user's task and their earlier requests in view, not only the most recent value. The model works out what a follow-up means from the conversation and the earlier tool calls; the application keeps the inputs and results and recalculates the same way every time. Research on conversational systems shows how often a request depends on what came before, and builds separate components that track each value the user has mentioned. [17](https://aclanthology.org/2020.emnlp-main.651/) [18](https://aclanthology.org/2020.tacl-1.36/) Use a separate task-state component only when the conversation and recorded calls do not provide enough reliable context.

**Keep the user's request separate from the agent's interpretation of it.** Keep the user's own words in the conversation history, rather than replacing them with a summary of what the agent understood, and record what the agent did as tool calls with their actual inputs. Then, when the agent has misunderstood, the model can see the difference, and a correction applies to what the user asked. Suppose a user asked for each holding's return over 20 days and the agent compared account balances instead. "Sorry, 30 days" then means 30-day returns, not a 30-day balance comparison. [19](https://aclanthology.org/2023.sigdial-1.52/)

## Make results meaningful

**Say in each tool result what its numbers mean.** The agent will describe whatever numbers it receives, so the result has to say what they measure. A change in an account balance includes deposits and withdrawals as well as market movement, so it is not a return; if the tool result does not say so, the agent may call it one. A drop in open support tickets can come from closing them or from moving them to another team. Put the meaning, the scope, the dates, and the units next to the numbers.

**When a tool rejects a request, say what it can do instead.** If the agent asks for a 20-day return and the tool supports only one month, three months, year to date, one year, and three years, the error should list those choices. The agent can then pick one or ask the user, rather than make up an answer.

**Make the change the user asked for.** When a user says "the dentist's phone number is wrong, it should be 555-0142," the agent should update the number, not save a note saying the number is wrong. If the user has not given the correct value, open the editor for that field or ask for it. If the agent makes a wrong change, it should say so and offer to undo it.

**Handle every item the user asked about.** "Remind me before each meeting with the clients on my priority list" means every client on that list. Changing one record correctly still fails the job if the others are missed. The [tool design chapter](tools.md) describes one way to make this reliable: let the agent name the whole group, and let the tool's code find its members.

**Say what happened and what comes next.** After a job, tell the user what was done, what was not, and what happens next, based on what actually happened rather than what the agent expected. "Reminders saved; two clients have no meeting scheduled yet; the app will check again tomorrow" makes clear that turning on a reminder is not the same as finding a date. [4](https://www.nngroup.com/articles/ten-usability-heuristics/)

**Let the application decide where feedback appears.** The application's code, not the model, should decide how a result is shown. Confirm a change where the user can see it. When a user asks to switch to dark mode, the screen turning dark is the confirmation; a chat message saying "dark mode is now on" adds nothing. Keep the user's attention for questions and problems. [2](https://martinfowler.com/eaaDev/uiArchs.html) [5](https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/) [6](https://www.w3.org/WAI/WCAG21/Understanding/status-messages.html)

**Tell, show, or do, depending on the request.** "Where do I change my cancellation policy?" gets directions and an offer to open the setting. "Take me to that setting" opens it. "Set the fee to twenty dollars" changes it. The agent chooses from what the user asked this time, not from what it did last time. When it opens a screen, it should say so only after the application confirms the screen is open, and it should not lose the conversation or anything the user has not yet saved. [3](https://www.microsoft.com/en-us/research/publication/principles-mixed-initiative-user-interfaces/)

## Work in the application people already know

**Work inside the forms, documents, and spreadsheets people already know.** Forms, documents, spreadsheets, presentations, and calendars have been refined over decades as ways to enter, check, and review information. Each carries rules and habits: a form marks what is required and checks it before submission; a spreadsheet keeps every number traceable to its source; a calendar shows a conflict at a glance. A chat reply loses most of that. Let the agent fill in a form, edit a document, or move around a spreadsheet, rather than replace them with conversation. Their own rules still apply: a required field is required whatever fills it, and a formula still calculates. The chat answers what the form or spreadsheet cannot: why a total moved, which fields are missing, what changed since last week.

**Show the agent's changes the way the document or spreadsheet already shows changes.** In a document, as tracked edits; in a spreadsheet, as highlighted cells; in a form, as fields marked as suggested. Then people review the agent's work the same way they review anyone else's.

**For a review, show the item itself and leave the decision to the person.** When people are asked to review something, put the item itself on screen, with the agent beside it to explain and point. Keep the decision on the screen's own controls, such as Approve and Reject, and have the agent point to evidence rather than give a verdict, so the review does not turn into trusting the agent's summary.

**Combine applications without bypassing their rules.** An agent could combine calendar events with company notes from another application to prepare meeting briefings. Each application still controls its own reads and writes, and the connection needs permission to move data between them. Plan for partial completion when one application succeeds and another fails.

!!! practice "Practice — add a follow-up"
    Write a likely request for your chosen job and one short follow-up. Underline what the
    follow-up changes. List what must stay the same and what application state the agent
    needs to interpret it. If two interpretations remain reasonable, write the question
    the agent should ask before acting.

Next, [define authority and recovery](authority.md) for the actions the agent may propose.
