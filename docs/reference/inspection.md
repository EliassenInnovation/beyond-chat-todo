# Inspect capabilities and execution

When an application needs portable inspection, connect three kinds of records: what the application can do, what a particular caller was offered, and what actually executed. A reusable inspection tool should be able to join these records without interpreting tool names or scraping the interface. The format below is one proposed application contract. Adapt it to your architecture and existing tracing infrastructure, and document which parts you adopt. It is not an MCP or observability standard. The principles are to preserve identity, actual outcomes, and evidence coverage; the field names illustrate one implementation.

Build on established observability. Use existing instrumentation, collectors, storage, and access controls. OpenTelemetry supplies a collection and export foundation with guidance on sensitive data; platforms such as Langfuse provide trace access controls, masking, and retention. [OpenTelemetry: handling sensitive data](https://opentelemetry.io/docs/security/handling-sensitive-data/) [Langfuse: access control](https://langfuse.com/docs/administration/rbac) For model and agent spans, use the OpenTelemetry GenAI semantic conventions, which cover agent operations (`create_agent`, `invoke_agent`), MCP spans, and a `gen_ai.evaluation.result` event for evaluator results. [OpenTelemetry: GenAI conventions](https://github.com/open-telemetry/semantic-conventions-genai) They are marked Development and the repository had no release as of October 3, 2026, so expect names to change and record the convention version used. Installing an SDK does not establish secure access. This contract adds application meaning those systems cannot infer: stable capability identity, offered-tool snapshots, trusted authorization outcomes, and committed state changes. It requires no new tracing protocol, authentication system, collector, or viewer.

| Responsibility | Owner |
| --- | --- |
| Trace transport, storage, viewer authentication, access controls, retention and deletion | Established observability infrastructure, configured for the deployment |
| Which data may be captured or exported; action identity, caller context, validation and actual effects | Application capability and shared execution layers |
| Pause, overrides, replay, undo and other debugging actions | Explicit application capabilities with separate execution authorization |

Represent the fields below using existing spans, events, attributes, and protected payload references where practical. Reuse supported semantic conventions and identify their version; keep additional fields in a documented application namespace. The field names define the logical contract; they do not require duplicating native records.

Keep inspection private and scoped. Enabling instrumentation must not expose a public endpoint, enable payload capture, or grant a debugging agent trace access. Start with necessary execution metadata; capture content only under explicit policy. Keep app, user, and workspace boundaries intact when aggregating. Collector ingestion credentials must not grant trace-reading or execution privileges. Filter prohibited data before it leaves the application; backend masking is additional protection. Record authorization outcomes as decisions or protected references, never credential or approval-token contents. Retrieved traces are untrusted material for a debugging agent.

Register actions with their owner. Each capability declares its actions alongside their implementation. Registration binds an action descriptor to its handler, input and output validation, and policy. Reject duplicate action IDs and unresolved handlers at startup. A registry can be a collection of ordinary modules and functions; it need not be a separate service or expose MCP.

An action is the stable unit of invocation. A capability groups related actions: `record.notes.read`, `record.notes.open_editor`, and `record.notes.replace` belong to `record.notes`. Opening an editor changes the screen; replacing notes changes stored data. Declare their inputs, results, and effects separately, even if one interface groups them under a single control.

Export a versioned catalog through an in-process function or serialized export; no network discovery endpoint is required. The following fields illustrate an export boundary:

| Record | Required fields and meaning |
| --- | --- |
| Catalog | `contract_version`, `app_id`, `app_version`, `catalog_revision`, `actions`. App and action IDs are stable; the revision identifies the exact catalog contents. |
| Action | `action_id`, `capability_id`, `action_version`, `title`, `description`, `input_schema`, `output_schema`, `effects`, `surfaces`, `policy_ref`, `recovery`. Schemas declare their JSON Schema dialect. The description states purpose, limits, and distinctions from neighboring actions. |
| Effects | A nonempty array drawn from `read` (reads data), `screen` (changes what the application's screen shows), `write` (changes stored data, in this application or another system), and `external` (reaches a system outside the application, whether to read or to write). Declare all that apply; an action that changes data in another system declares both `write` and `external`. Do not infer behavior from verbs such as get or update. |
| Surfaces | Supported callers: `ui`, `embedded_agent`, `cli`, or `mcp`. These describe possible exposure, not current authorization. |
| Recovery | `mode`: `none`, `undo`, or `compensate`, plus an explanation of limits. Declaring recovery does not establish that a particular call can still be recovered. |

An implementation adopting this exact shape can identify it as contract version `1`. A breaking export change increments `contract_version`; an incompatible action change increments `action_version`; any descriptor change, including wording, changes `catalog_revision`. Never reuse an action ID for a different purpose. Document extensions under `extensions`; consumers tolerate unknown extension fields.

Export MCP tool annotations from the catalog. When an action is served over MCP, derive its annotations from the descriptor so an MCP host shows accurate risk labels: `readOnlyHint` says whether the action modifies its environment, so it is true when `effects` contains no `write` and no `screen`; `openWorldHint` says whether the action reaches outside systems, so it is true when `effects` contains `external`. Set `openWorldHint` to false for every other action: MCP's default for an unannotated tool is true. The two are set independently: a web search is read-only and reaches an outside system. The catalog does not yet say whether a write only adds or may destroy, or whether repeating a call has no further effect, so declare those under `extensions` and map them to `destructiveHint` and `idempotentHint`. `recovery` does not set `destructiveHint`: an undoable deletion is still destructive. Without these declarations, leave the MCP defaults (`destructiveHint` true, `idempotentHint` false). Annotations are hints a client must treat as untrusted unless the server is trusted; they never replace the policy check at execution (Check 3.3). [MCP specification: tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)

Record the tools each caller was actually offered. A full catalog does not prove that a model saw a tool. For each model request, record `model_request_id`, `catalog_revision`, and a `tool_surface` snapshot of the exact provider-facing names, descriptions, and schemas delivered, subject to the capture policy. Map each exposed tool to its `action_id` and `action_version`. Keep unsupported, policy-denied, and temporarily unavailable actions distinguishable; recheck policy at execution, since a listing is neither authorization nor a reservation. Caller identity and approval evidence come from the adapter's trusted context, never from model-supplied arguments.

## Route execution and observation through the same boundary

All supported callers invoke the registered action through shared execution. Adapters translate arguments and results; they do not call a second implementation or bypass validation. Internal composition may call another capability through this boundary as a child invocation.

Shared state describes the screen; it does not write stored data. In frameworks such as AG-UI, the frontend and the agent both read and modify a shared state object. [AG-UI: state management](https://docs.ag-ui.com/concepts/state) Any change to stored data that arrives through that state must be executed as a registered action through shared execution, or it bypasses policy, validation, and undo.

```text
UI / embedded agent / CLI / MCP adapter
  → resolve action and establish trusted caller context
  → record invocation; check policy and validate input
  → execute the owning handler; validate result and record actual effects
  → complete the persistence/history guarantees required by that action
  → return the application outcome and emit its observation
```

Publish structured observations at this boundary, for successes as well as errors, distinguishing these identities:

| Field | Meaning |
| --- | --- |
| `interaction_id` | One user interaction, potentially several model requests and actions. |
| `model_request_id` / `tool_call_id` | Provider identifiers where applicable; null for direct UI actions. |
| `invocation_id` / `parent_invocation_id` | Unique execution attempt and its enclosing invocation. Retries get new IDs linked through `retry_of`. |
| `action_id`, `action_version`, `catalog_revision` | The exact application contract used. |
| `surface` / `actor_kind` | Entry surface and initiator (`human`, `agent`, or `system`), assigned by application code. |
| `trace_id` / `span_id` | Optional correlation with existing tracing; not substitutes for application identities. |

Represent start and finish with a native span lifecycle or explicit `started` and `finished` records carrying an `event_id`, `invocation_id`, timestamp, and sequence number. Completion includes duration, permitted input and result or references, and status: `succeeded`, `rejected`, `failed`, `cancelled`, or `pending`, with an application error code distinguishing invalid input, policy denial, conflicts, and execution errors. Keep execution status separate from effects: report `effect_status` as `none`, `committed`, `partial`, or `unknown`, with change and revision references. An interrupted process may leave a start with no finish; a viewer must show an incomplete observation, not invent an outcome.

Expose context deliberately. When capture is authorized, record or reference the messages actually sent, model and configuration, application context supplied, response, and usage. Otherwise record permitted metadata and mark content omitted. Keep records unaltered for their retention period; deletion that policy authorizes is a separate, recorded step. Each payload declares `capture_state` (`complete`, `redacted`, `omitted`, or `truncated`). Record sampling and dropped events where known; absence of a trace is not proof nothing executed. Observation-export failure must never turn a committed action into a reported failure or trigger its retry. For MCP, distinguish the local client call from execution inside the remote server, and mark remote effects as unobserved when only one side is instrumented.

## Declare inspection support and test the contract

Export a support manifest naming which of `catalog`, `tool_surface`, `model_requests`, `invocations`, `state_changes`, and `presentation_context` are implemented, with uncovered paths and capture restrictions, so a viewer can show which paths were observed and which were not. Observation grants no execution authority: pause, argument replacement, overrides, replay, and undo are separately authorized capabilities, and replaying a trace must never rerun writes against live state by default.


Start with one capability and prove the full path before extending coverage. Adapt
[Checks 1.7–1.11](../principles/implementation.md#make-the-capability-registry-inspectable)
to the inspection features you choose.

