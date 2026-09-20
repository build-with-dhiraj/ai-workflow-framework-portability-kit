# Building with Agentflow V2

Agentflow V2 arrived in `3.0.0` (May 2025) as a rewrite, not a migration. V1 delegated graph
logic to LangGraph; V2 uses native Flowise nodes with its own execution engine. Both still run,
and both are now permanent, because nothing will be removed from an archived project.

**There is no V1 to V2 converter.** The UI shows a banner recommending migration and nothing
else. Migration is a manual rebuild. Since V1 will never be removed, an inherited V1 flow that
works can be left alone; rebuild when you want V2 features, not out of urgency.

## Node reference

Fifteen node types. The identifier pattern is `<camelCaseName>Agentflow`, and instances are
suffixed `_0`, `_1` in the order they were added, which is how they are referenced in prompts.

| Node | Identifier | Use it for | Output anchors |
|---|---|---|---|
| Start | `startAgentflow` | Mandatory entry. Declares Flow State. Chat or Form input | one |
| LLM | `llmAgentflow` | A direct model call, or structured extraction | one |
| Agent | `agentAgentflow` | Autonomous reason/plan/act with tools and knowledge | one |
| Tool | `toolAgentflow` | Run one named tool deterministically, no model chooses | one |
| Retriever | `retrieverAgentflow` | Query a Document Store by similarity | one |
| HTTP | `httpAgentflow` | Outbound HTTP call | one |
| Condition | `conditionAgentflow` | Deterministic branch on a comparison | one per outcome |
| Condition Agent | `conditionAgentAgentflow` | Model-driven routing over named scenarios | one per scenario |
| Iteration | `iterationAgentflow` | For-each over an array, with a nested sub-flow | one, after all items |
| Loop | `loopAgentflow` | Jump back to an earlier node | none forward |
| Human Input | `humanInputAgentflow` | Pause for approval or feedback | two: proceed, reject |
| Direct Reply | `directReplyAgentflow` | Reply and end this path | none |
| Custom Function | `customFunctionAgentflow` | Server-side JavaScript | one |
| Execute Flow | `executeFlowAgentflow` | Call another flow as a sub-workflow | one |
| Sticky Note | `stickyNoteAgentflow` | Annotation, no execution | none |

`executeFlowAgentflow` is the one people forget exists. It takes chatflow API credentials, a
target flow, an input, a per-call `Override Config` and optionally a different `Base URL`.

Reach for it knowing its limits, because they are not documented and they bite exactly when you
use it to tame a large flow. Flow state does **not** propagate into the child: the sub-flow starts
with its own state declared by its own Start node, so anything it needs must be passed as input
rather than assumed shared. And it has a reported defect where the node returns an identifier
rather than the child's output, which turns a working split into a silent data loss one refactor
later. Neither will be fixed upstream.

So splitting a flow is a real option, but verify what actually comes back before building on it,
and pass state explicitly. If a flow is growing past comprehension and you own a service, moving
the orchestration into your own code is now the more durable answer than either splitting the flow
or adding another branch.

## Flow State, and the rule that catches everyone

State is a key-value store shared by every node within **one execution**. It is created at the
start of a run and destroyed at the end, so it does not persist across sessions, and concurrent
executions each get their own.

The rule that produces most "my data disappeared" reports: **every key must be declared in the
Start node's Flow State parameter**, with an initial value, even an empty one. Nodes with an
`Update Flow State` setting can modify keys that already exist and **cannot create new ones**.
So a downstream write to an undeclared key silently does nothing.

Nodes that can update state: LLM, Agent, Tool, HTTP, Retriever, Custom Function, Execute Flow.

Updates are configured as key/value pairs where the value usually references the node's own
output:

```json
[ { "key": "classification", "value": "{{ output.category }}" } ]
```

## The template vocabulary

Typing `{{` in any variable-accepting field lists what is available, which is faster than
remembering. The full set:

| Syntax | Means |
|---|---|
| `{{ question }}` | The incoming user question |
| `{{ $form.<field> }}` | A Start-node Form Input field |
| `{{ $flow.state.<key> }}` | Read flow state |
| `{{ $vars.<name> }}` | An instance Variable |
| `{{ <nodeId> }}` | The whole output of an earlier node, e.g. `{{ llmAgentflow_0 }}` |
| `{{ <nodeId>.output.<key> }}` | One key of an earlier node's structured output |
| `{{ output }}` / `{{ output.<key> }}` | The **current** node's output, valid inside Update Flow State |
| `{{ $iteration }}` / `{{ $iteration.<key> }}` | The current item inside an Iteration block |

The distinction between `{{ output }}` and `{{ nodeId }}` is worth internalising: `output` is
self-referential and only meaningful while configuring the node that produces it.

**The braces are for text fields only.** Everything above is template interpolation into a string,
so it applies to prompts, URLs, headers and condition values. Inside a Custom Function's JavaScript
body you are in real code and the same reference is a variable: `$flow.state.category`, no braces.
Writing `{{ $flow.state.category }}` in a function body is a syntax error, and writing
`$flow.state.category` in a prompt renders that literal text to the model. Both failures are quiet
in their own way, and it is the single most common confusion when someone moves logic between a
prompt and a function.

## Getting a reliable branch out of a model

A classification that drives a branch has to be machine-readable, so use the LLM node's
**JSON Structured Output** to declare the keys and types rather than asking for JSON in prose
and hoping. Then write the field into state with `Update Flow State`, and branch on the state
key with a Condition node.

That ordering matters. Branching directly on a raw model response couples your control flow to
free text, and the failure is intermittent, which is the worst kind.

Choose between the two branch nodes on whether the decision is expressible:

- **Condition** when you can write the comparison. Deterministic, free, debuggable.
- **Condition Agent** when the routing genuinely needs judgment. Each scenario is a natural
  language description and gets its own anchor.

Prefer Condition where both would work. A deterministic branch that you can read is worth more
than a model call, and one fewer model call in a loop is real latency.

Known rough edge: conditions have a reported bug when two or more branches converge on the same
downstream node. If a branch behaves inconsistently at a merge point, that is a candidate cause,
and it will not be fixed upstream.

## Custom Function nodes

Server-side JavaScript. Input Variables are declared with names and bound to values, then
referenced in the body with a `$` prefix. Available globals: `$<inputName>`, `$flow.sessionId`,
`$flow.chatId`, `$flow.chatflowId`, `$flow.input`, the whole `$flow.state` object, `$vars.<name>`,
and `require()` for built-in plus allowlisted external modules.

**The function must return a string.** Returning an object is a common cause of a node that
appears to run and produces nothing useful downstream; serialise it.

**Do not have a Custom Function write flow state as its main effect.** Mutating `$flow.state`
directly from the body is reported not to persist reliably to the next node; the dependable route is
to return the value and let the node's own `Update Flow State` setting record it, which is the same
mechanism every other node uses. If a function seems to run correctly and a downstream node reads a
stale value, this is the first thing to check rather than the declaration rule above.

Watch type coercion at the boundary too. Values arriving through interpolation reach the body as
strings, so a state key holding `false` tests as the truthy string `"false"`, and a numeric
comparison against `"10"` is a string comparison. Coerce explicitly at the top of the function
rather than trusting the type you think you stored.

If `require` fails with `NodeVM Execution Error: VMError: Cannot find module`, the module is not
allowlisted. Add it to `TOOL_FUNCTION_EXTERNAL_DEP` rather than reaching for `ALLOW_BUILTIN_DEP=true`,
which opens far more than you need.

A related contract worth not confusing: the **Custom Document Loader** may return either a string
or an array of `{pageContent, metadata}`, and has a hard **10 second timeout**.

## Where to put logic

The recurring judgment call is how much goes in a Custom Function versus a service you own.
Some things push you out of the graph:

- Anything needing tests, code review, or a rollback story. Flows have no version history a
  reader can consult, and no diff in the product.
- Anything another system also needs to call.
- Anything where a silent fallback would be unacceptable.

And some things belong in the graph: orchestration you want visible, steps a non-engineer should
be able to inspect, and anything you expect to tune by editing a prompt.

The archive sharpens this. Logic in the graph now sits on frozen infrastructure, and logic in
your own service does not. That is a reason to keep new load-bearing work outside the flow, and
to treat existing flows as things to read and eventually port rather than extend indefinitely.
