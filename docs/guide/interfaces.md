# Connect interfaces to the same capabilities

Shared capabilities preserve business meaning across callers. Each interface still needs an adapter: a control and result display for the UI, a tool schema and result for an agent, or commands and help for a command line. Add an interface when a real job requires it. An embedded agent does not require an HTTP API or an MCP server.

## Keep ownership explicit

The capability owns domain inputs, validation, effects and results. Shared execution applies common policies and transaction boundaries. The interface translates the caller's request and presents the result. This separation follows the [ports-and-adapters pattern](https://alistair.cockburn.us/hexagonal-architecture); a registry is one way to describe the shared contracts.

Different interfaces may group controls differently. A settings screen may offer separate font-size and contrast controls, while an agent tool accepts both for “make this easier to read.” Both still use the same operations. A command called “add” must not replace existing data when the corresponding UI operation preserves it.

## Observe and operate the screen

The embedded agent needs both an observation of what the person sees and named actions that can change that view. A central state store or state machine can coordinate selection, navigation and filters. Each UI component declares the actions it owns; clicks and agent calls use the same dispatch. Keep screen state distinct from saved domain data.

Offer ways to explain a control, point to it, open its screen, and perform its operation when appropriate. Build directions from actual control labels. Preserve unsaved work and conversation when navigating. Use screenshots and simulated clicks when a suitable application interface is unavailable, rather than making them the default integration for your own app.

## Separate listing from execution

An embedded agent shares the person's screen. An external agent may only need data reads and writes; a headless process has no screen to operate. Offer screen actions only where they can work and where the person expects them. Explicitly designed external screen control is possible, but should not be an accidental consequence of exposing the application's tools.

Listing determines which tools a model is offered. Execution policy determines which operations a caller may run, including calls made directly by name. A data read omitted from the embedded agent's list may still be permitted. An operation forbidden by policy must be refused even if the caller knows its name.

## Return a view and a complete text answer

An external chat application can be another client of your application, much as a mobile
app can be another client of an existing service. **MCP**, the Model Context Protocol, gives
that client a way to discover and call tools. It does not replace the application's access rules.


An MCP Apps view is an interactive page supplied with a tool's result for a supporting host to display in the conversation. It is separate from controlling the original application's screen. The todo sample does not implement an MCP server; these are requirements for adapting the shared capabilities to that interface.

Negotiate view support when the client connects. Send view metadata only to clients that announce support. Supply a complete text answer to both kinds of client, including every figure the view presents. Compute the figures once in application code, with dates, units and missing-data indicators, and use that result for both presentations.

When a view is supplied, tell the model that the person can already see it and ask for useful interpretation rather than repetition. Keep the text complete even then, because rendering may fail. Test both connections: view support present and absent. Check that presentation metadata is scoped to the connection, so one client's capabilities do not affect another's result.

!!! consider "Consider — does another interface serve a real job?"
    Write down who would use an external agent or command line for your chosen job and what
    they would gain. If there is no concrete benefit, keep the embedded interface for now.
    If there is, list which data and screen operations that caller actually needs.

The [acceptance checks](../principles/implementation.md) provide a review reference. Continue with [the running sample](start.md).
