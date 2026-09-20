# Calling Flowise from code

## Auth and the base shape

Everything sits under `/api/v1`, default port 3000. The header is:

```
Authorization: Bearer <api-key>
```

Keys are created in the dashboard's API Keys section and assigned per flow. There are no scopes
and no documented expiry. `x-api-key` appears in some deployments and is not in the documentation,
so if Bearer returns 401 or 403 against an instance you do not control, that is worth trying
before assuming the key is wrong.

**Flows are public by default.** Anyone holding the chatflow id can call it until you assign a key.

## Endpoints, verified live against a 3.0.12 instance

Verified by probe, with the response shape actually returned:

| Path | Returns |
|---|---|
| `GET /api/v1/version` | `{version}` |
| `GET /api/v1/chatflows` | array of every flow. `?type=AGENTFLOW` filters |
| `GET /api/v1/chatflows/{id}` | one flow |
| `GET /api/v1/nodes` | array of every available node type, 299 on a stock install |
| `GET /api/v1/tools` | array |
| `GET /api/v1/variables` | array |
| `GET /api/v1/credentials` | array, names and types only, never secrets |
| `GET /api/v1/assistants` | array |
| `GET /api/v1/executions` | `{data, total}`, paged |
| `GET /api/v1/document-store/store` | array |
| `GET /api/v1/marketplaces/templates` | array, 50 on a stock install |
| `GET /api/v1/settings` | `{PLATFORM_TYPE}`, tells you open source vs enterprise |
| `GET /api/v1/apikey` | array |
| `GET /api/v1/upsert-history/{id}` | array |
| `GET /api/v1/ping` | plain text health check |
| `GET /api/v1/ip` | the client IP as the server sees it, for calibrating `NUMBER_OF_PROXIES` |
| `GET /api/v1/metrics` | Prometheus scrape target, requires the API key |

Two that return **412 without an id**, which reads like an auth failure and is not:
`/api/v1/stats` and `/api/v1/leads`. Both want `/{chatflowId}`.

**`/api/v1/agentflows` does not exist.** It returns the single-page app's HTML with a 200 status.
A JSON parse failure on a 200 is the tell. Use the chatflows route with a type filter.

Writes: `POST`/`PUT`/`DELETE` on `/chatflows`, `/tools`, `/variables`, `/assistants`,
`/document-store/store`. Executions, credentials and API keys have no documented CRUD API.

## Predictions

```
POST /api/v1/prediction/{chatflowId}
```

```json
{
  "question": "How do I reset my password?",
  "streaming": true,
  "overrideConfig": { "sessionId": "user-42", "vars": { "userId": "42" } },
  "history": [{ "role": "userMessage", "content": "hi" }]
}
```

`question` is required unless the flow uses Form Input, in which case send `form` with the form
field names as keys. `uploads[]` carries files, with `type` one of `audio`, `url`, `file`,
`file:rag`, `file:full`.

A non-streaming response returns `{text, json?, question, chatId, chatMessageId, sessionId?,
sourceDocuments?, usedTools?}`.

**Mint `chatId` yourself, and pass it on the first request.** It is how a conversation continues
and it is required to resume a paused human-in-the-loop execution, but you do not have to wait for
the server to tell you what it is. One line decides it, in `buildChatflow.ts` (verified on the
`3.0.12` tag, line 996):

```ts
const chatId = incomingInput.chatId ?? incomingInput.overrideConfig?.sessionId ?? uuidv4()
```

A caller-supplied `chatId` is used verbatim. So generate a UUID client-side, send it, and you own
the thread identifier from the start. That is worth more than it looks: it removes any need to read
the `metadata` event before you can continue a conversation, which is otherwise the most awkward
thing about consuming the stream.

Two consequences of that chain:

- **`overrideConfig.sessionId` becomes the `chatId`** when no `chatId` is sent. The two identifiers
  collapse, so code that sets only `sessionId` is also setting the chat id whether it meant to
  or not.
- `sessionId` is otherwise resolved independently, by `getMemorySessionId(memoryNode, incomingInput,
  chatId, isInternal)`, from the flow's memory node. It is not derived from `chatId`. They are
  separate concepts sharing one input slot, which is why this catches people.

The docs use `chatId` in examples while omitting it from the schema. That is a documentation
defect, not a hint that it is optional.

Note the documentation contains a `/api/v1/predictions/` example, plural. That path does not
exist; every other reference uses the singular.

## Streaming

### First: asking for a stream does not mean you get one

This is the failure that wastes the most time, because it presents as a client bug. The controller
decides in one branch (`controllers/predictions/index.ts:57-92`, verified on `3.0.12`):

```ts
const streamable = await chatflowsService.checkIfChatflowIsValidForStreaming(req.params.id)
const isStreamingRequested = req.body.streaming === 'true' || req.body.streaming === true
if (streamable?.isStreaming && isStreamingRequested) {
    // SSE: sets text/event-stream and streams
} else {
    const apiResponse = await predictionsServices.buildChatflow(req)
    return res.json(apiResponse)          // <- same URL, same 200, plain JSON
}
```

So a flow that is not stream-eligible answers your `"streaming": true` request with **ordinary JSON
on a 200**, with no error and no warning. An SSE reader pointed at that either hangs or fails to
parse, and the natural conclusion is that your parser is broken.

**Branch on the response `Content-Type` rather than on what you asked for.** A flow becomes
ineligible for reasons that have nothing to do with your request: post-processing enabled, a Custom
Function as the ending node, or a final LLM node with streaming off. Any of those can be introduced
by someone editing the flow, so a client that was streaming yesterday can be receiving JSON today
with nothing on your side changed.

Note also that `streaming` accepts the string `"true"` as well as the boolean, which is worth
knowing when the value arrives from a query parameter or a form.

### The events

The events are:

| Event | When |
|---|---|
| `start` | streaming begins |
| `token` | each token |
| `metadata` | after all tokens, before `end`, carries `chatId` and message ids |
| `sourceDocuments` | the flow returned vector-store sources |
| `usedTools` | the flow called tools |
| `error` | the prediction failed |
| `end` | finished |

The ordering is the one thing to design around: `metadata` arrives near the end, so a UI that waits
for `chatId` before it can send a follow-up cannot enable its input box until the answer has almost
finished. **Send your own `chatId` and the problem disappears** rather than being handled: you
already know the thread id, so `metadata` becomes optional and `end` is the only event your loop
must not miss. Prefer that to sequencing around a late event.

The SDKs yield objects of the shape `{event: "token", data: "..."}`, so the same loop handles
streaming and non-streaming responses.

One thing to check before shipping a stream to end users: intermediate agent events reach the
client. Depending on the flow and its settings the stream can carry `agentFlowEvent`,
`nextAgentFlow`, `calledTools` and similar, which expose node names and tool calls, so anyone with
devtools open can read your orchestration. Filter server-side to the events your UI renders instead
of proxying the stream through untouched.

Two operational notes. Streaming changed to SSE in `2.1.0`; an embed pinned below that will not
receive messages from a newer server. And in queue mode the stream is fed through Redis pub/sub,
which has a history of fragility, including a fix that was shipped and reverted in the same
release.

### From a Next.js route handler

Proxy it rather than calling from the browser, so the API key stays server-side:

```ts
const res = await fetch(`${process.env.FLOWISE_URL}/api/v1/prediction/${flowId}`, {
  method: "POST",
  headers: { "Content-Type": "application/json", Authorization: `Bearer ${process.env.FLOWISE_KEY}` },
  body: JSON.stringify({
    question,
    streaming: true,
    chatId,                       // your UUID, minted per conversation, so you never parse metadata
    overrideConfig: { sessionId: user.id, vars: { userId: user.id } },
  }),
});
return new Response(res.body, { headers: { "Content-Type": "text/event-stream" } });
```

Passing the user through has two routes and they behave differently. `sessionId` scopes
conversation memory, so it is what you want for "this user's thread". `vars` injects values the
flow can read as `$vars.userId`, which is what you want for personalisation inside prompts.

Note what happens if you drop the explicit `chatId` from that body: `overrideConfig.sessionId` takes
its place, so every conversation by the same user shares one chat id and their separate threads merge
in the stored history. Passing both keeps "which user" and "which conversation" independent, which is
almost always what a real app wants.

## overrideConfig, and why it silently does nothing

Three rules that account for nearly every surprise:

**It is disabled by default** since `2.1.4`, per property, in the flow's Security tab. The gate is
one condition, `if (incomingInput.overrideConfig && apiOverrideStatus)` (`buildChatflow.ts:179`), so
an override that has no effect is almost always this and not a malformed body.

**`sessionId` is exempt from that gate, and `vars` is not.** Session resolution happens at
`buildChatflow.ts:508`, before `getAPIOverrideConfig(chatflow)` is even called at line 546, so
`overrideConfig.sessionId` always lands. That asymmetry gives you a precise diagnostic: if
conversation memory is scoped correctly per user but prompts come back generic and unpersonalised,
the override toggle is off and only `sessionId` is getting through. Two symptoms, one cause, and it
is the fastest way to tell this apart from a flow that simply ignores its variables.

**Variables must already exist.** You cannot create a variable through `vars`, only override one
that is defined on the instance.

**Array-typed configs concatenate rather than replace.** Overriding an array property appends to
what is there. If you expect replacement you get both.

By default an override applies to **every node of that type**. To target one node, nest the node
id:

```json
"overrideConfig": {
  "llmMessages": {
    "llmAgentflow_0": [{ "role": "system", "content": "You are terse" }],
    "llmAgentflow_1": [{ "role": "system", "content": "You are thorough" }]
  }
}
```

The overridable keys per flow are shown behind the UI's **View API** button, which is the
authoritative list; the documentation does not publish a complete catalogue.

## Embedding

```html
<script type="module">
  import Chatbot from 'https://cdn.jsdelivr.net/npm/flowise-embed/dist/web.js'
  Chatbot.init({ chatflowid: '...', apiHost: 'https://flowise.example.com' })
</script>
```

Pin a version in production rather than tracking latest. `chatflowConfig` takes the same shape as
`overrideConfig`. `observersConfig` gives you `observeUserInput`, `observeMessages` and
`observeLoading` callbacks, which is how you wire the widget into your own analytics.

If the browser reports a missing `Access-Control-Allow-Origin` header, that is `CORS_ORIGINS` and
`IFRAME_ORIGINS` on the server, not a widget setting.

There is also `flowise-embed-react` on npm with `<FullPageChat>` and `<BubbleChat>` components.
It works and is entirely absent from the documentation, so treat its API as discovered rather
than specified.

## Moving flows between environments

There is no built-in promotion path, no version history and no diff. What people actually do:

1. Export each flow's JSON and commit it to a repository, ideally on a schedule rather than by
   hand. `flowise.mjs flow "<name>" --out flows/name.json` does this.
2. Diff exports to answer what changed, since the product will not tell you.
   `flowise.mjs diff old.json new.json` reports added, removed and changed nodes by label.
3. Import into the target instance, matching versions. The export format changed at `3.0.0` and
   is not backward compatible, so a `3.x` export cannot be imported into `2.x`.

Two things do not travel. Credentials are not exported, so they are recreated per environment.
And entity ids are preserved on some paths, which means an imported flow may keep its id and
collide, so check rather than assume.

Given the project is archived, the export is also your migration artifact. It preserves the
design faithfully and is not runnable outside Flowise, so treat it as the specification you would
reimplement from, and keep it current now rather than when you need it.
