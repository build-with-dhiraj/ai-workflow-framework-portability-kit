# Calling a Flowise chatflow from Next.js with token streaming + a user ID

**Short version:** one `POST /api/v1/prediction/{chatflowId}` with `streaming: true`, proxied through a Next.js route handler. The user ID rides in `overrideConfig` — `vars.userId` for the prompt, `sessionId` for memory scoping. What comes back is SSE, but in a **non-standard frame shape** (`message:\ndata:{...}`), and Flowise will **silently answer with plain JSON instead** if your flow isn't streamable. Both of those bite people, so they're covered in detail below.

---

## 1. Two things to do in the Flowise UI first

Skip these and you get a `200 OK` with a perfectly plausible answer and **no personalisation at all** — the hardest version of this bug to spot.

**a. Create the variable.** Flowise sidebar → **Variables** → add `userId`, type **Runtime**.
- `Static` = value stored in Flowise, not overridable.
- `Runtime` = value comes from `process.env` **or** an API override. You need Runtime.

Reference it inside the flow as:
- `{{$vars.userId}}` — in any text field: system message, prompt template, tool description.
- `$vars.userId` — inside Custom Tool / Custom Function JS code.

**b. Allow the override.** Open the chatflow → **Settings** (top right) → **Configuration** → **Security** tab → enable override configuration and tick `userId`.

This is not optional decoration. In `packages/server/src/utils/index.ts` the override is applied behind:

```ts
if (overrideConfig && apiOverrideStatus) {
    flowNodeData = replaceInputsWithConfig(flowNodeData, overrideConfig, nodeOverrides, variableOverrides)
}
```

If `apiOverrideStatus` is false, the **entire** `overrideConfig` object is dropped without an error. Each runtime variable is then checked a second time against a per-variable `enabled` flag, so ticking the master toggle but not the variable fails the same silent way.

**One exception worth knowing:** `overrideConfig.sessionId` is read straight off the request body in `getMemorySessionId()` *before* the graph is built, so it is **not** gated by that toggle. Memory scoping works even with overrides disabled — `vars` does not. If your memory is keyed correctly but the prompt isn't personalised, that asymmetry is your culprit.

---

## 2. The request

```http
POST /api/v1/prediction/8f4d1b2e-3c7a-4e91-b0d5-1a2b3c4d5e6f HTTP/1.1
Host: flowise.internal:3000
Content-Type: application/json
Authorization: Bearer REDACTED

{
  "question": "What should I read next?",
  "streaming": true,
  "overrideConfig": {
    "sessionId": "conv_7c2a",
    "vars": { "userId": "user_9f31" }
  }
}
```

Body fields that matter here:

| Field | Notes |
|---|---|
| `question` | The user's message. (Agentflow V2 flows started by a form use `form` instead.) |
| `streaming` | `true` **or** the string `"true"` — the server accepts both: `req.body.streaming === 'true' \|\| req.body.streaming === true`. |
| `overrideConfig.vars` | Runtime variables. This is how `userId` reaches `{{$vars.userId}}`. Requires step 1b. |
| `overrideConfig.sessionId` | Keys the **memory node**. Must be a string or you get a `400 Invalid sessionId: must be a string`. |
| `chatId` | Groups messages in Flowise's chat log / DB. Optional. |
| `history` | `[{ role: "userMessage" \| "apiMessage", content: "..." }]` — only if you're managing history yourself instead of using a memory node. |
| `uploads` | `[{ type: "file" \| "file:rag" \| "file:full" \| "url" \| "audio", name, data, mime }]` |

**`sessionId` vs `chatId` — pick deliberately.** Resolution order is verified in source:

- Memory key: `overrideConfig.sessionId` → else `chatId` → else generated.
- Chat log id: `chatId ?? overrideConfig.sessionId ?? uuidv4()`.

So if you set `sessionId = userId` and never pass `chatId`, **every conversation that user ever has collapses into one memory buffer and one chat log.** Usually what you want is:

```jsonc
"overrideConfig": {
  "sessionId": "conv_7c2a",          // per-conversation → separate memory per thread
  "vars": { "userId": "user_9f31" }  // per-user → personalisation
}
```

Use `sessionId = userId` only if you genuinely want one endless cross-device thread per person.

---

## 3. What you actually get back on the wire

### Branch A — streaming (what you want)

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
Transfer-Encoding: chunked
```

Then frames. This is the exact byte shape — note the first line of every frame:

```
message:
data:{"event":"start","data":""}

message:
data:{"event":"token","data":"Based"}

message:
data:{"event":"token","data":" on"}

message:
data:{"event":"token","data":" your"}

:heartbeat

message:
data:{"event":"usedTools","data":[{"tool":"library_search","toolInput":{"userId":"user_9f31"},"toolOutput":"..."}]}

message:
data:{"event":"metadata","data":{"chatId":"c1f0e8a2-...","chatMessageId":"9ab2f4c1-...","question":"What should I read next?","sessionId":"conv_7c2a","memoryType":"Buffer Memory"}}

message:
data:{"event":"end","data":"[DONE]"}
```

…and the connection closes. Every frame is written by exactly one line of Flowise:

```ts
this.safeWrite(chatId, 'message:\ndata:' + JSON.stringify({ event: eventType, data }) + '\n\n')
```

**Five things about this format that will cost you an hour each if you don't know them:**

1. **`message:` is a bare, valueless line, and the real event name is inside the JSON.** It is not an SSE `event:` field. Per the SSE spec, `message:` is an unrecognised field name and gets ignored, so the event type stays the default `message` and the payload is the `data:` line. Consequence: **do not** switch on SSE event types — parse the JSON and switch on `.event`.
2. **No space after `data:`.** `line.slice(5)` is the payload. (Trim anyway; it costs nothing.)
3. **`:heartbeat` comment frames** appear on idle connections. Any line starting with `:` must be skipped, as must the bare `message:` line.
4. **`metadata` arrives at the *end*, not the start** — the server calls `streamMetadataEvent` only after the flow resolves. If you need `chatId` to continue the conversation, either generate and send your own, or read it from this late event *after* the tokens have all rendered.
5. **Errors arrive in-band under HTTP 200.** Headers are flushed before the flow runs, so a mid-flight failure is `{"event":"error","data":"..."}`, not a 500. `res.ok` tells you nothing about whether the answer succeeded.

Event catalogue (from `SSEStreamer.ts`) — you'll normally only handle the first four:

| Event | `data` payload |
|---|---|
| `start` | `""` — first token is imminent |
| `token` | string fragment — **this is what you append to the UI** |
| `error` | error message string |
| `end` | `"[DONE]"`, then the stream closes |
| `metadata` | `{ chatId, chatMessageId, question, sessionId, memoryType, followUpPrompts?, flowVariables?, action? }` |
| `thinking` | reasoning-model thinking text |
| `sourceDocuments` | RAG chunks with metadata |
| `usedTools` / `calledTools` | `[{ tool, toolInput, toolOutput }]` |
| `artifacts` | generated files/images |
| `agentReasoning`, `nextAgent` | Multi/Sequential Agent progress |
| `agentFlowEvent`, `agentFlowExecutedData`, `nextAgentFlow` | Agentflow V2 node-level progress |
| `action` | human-in-the-loop prompt — resume with `humanInput` |
| `usageMetadata` | token counts |
| `abort` | run cancelled |
| `fileAnnotations`, `tool`, `tts_*` | annotations, tool trace, text-to-speech |

### Branch B — the silent JSON fallback

Same URL, same method, same `streaming: true`, same `200`. If the flow can't stream, Flowise just does `res.json(apiResponse)`:

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
```

```json
{
  "text": "Based on your reading history, I'd suggest...",
  "json": null,
  "question": "What should I read next?",
  "chatId": "c1f0e8a2-...",
  "chatMessageId": "9ab2f4c1-...",
  "sessionId": "conv_7c2a",
  "memoryType": "Buffer Memory",
  "sourceDocuments": null,
  "usedTools": null
}
```

A parser expecting SSE gets one useless blob and no tokens. **Branch on the response `Content-Type`, never on the fact that you asked for streaming.**

A flow is judged non-streamable when any of these hold (verified in `checkIfChatflowIsValidForStreaming`):

- **Post-processing is enabled** in the chatflow config — unconditional `isStreaming: false`. Easiest one to trip over.
- The graph has a **Custom Function ending node**.
- The final LLM/chain node doesn't support streaming.

Always streamable: `AGENTFLOW` type flows, and Multi Agents / Sequential Agents ending nodes.

You can ask ahead of time:

```bash
curl -H "Authorization: Bearer $FLOWISE_API_KEY" \
  http://flowise.internal:3000/api/v1/chatflows-streaming/8f4d1b2e-...
# → {"isStreaming":true}
```

---

## 4. Next.js implementation

Two hard constraints shape this, and both mean you need a server route in the middle:

- **The Flowise API key must never reach the browser.** So no calling Flowise from a client component.
- **The user ID must come from the server-side session, never from the request body.** If the browser supplies `userId`, any user can set it to someone else's and read their personalised context. This is the whole security story of this feature.

### `app/api/chat/route.ts`

```ts
import { auth } from '@/auth' // whatever gives you the session server-side

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'
export const maxDuration = 60 // Vercel: default is far shorter than an LLM answer

export async function POST(req: Request) {
  const session = await auth()
  if (!session?.user?.id) return new Response('Unauthorized', { status: 401 })

  const { question, sessionId } = await req.json()
  if (typeof question !== 'string' || !question.trim()) {
    return new Response('Bad request', { status: 400 })
  }

  const upstream = await fetch(
    `${process.env.FLOWISE_URL}/api/v1/prediction/${process.env.FLOWISE_CHATFLOW_ID}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.FLOWISE_API_KEY}`
      },
      // propagates client disconnect upstream so an abandoned answer stops burning tokens
      signal: req.signal,
      body: JSON.stringify({
        question,
        streaming: true,
        overrideConfig: {
          sessionId: String(sessionId ?? crypto.randomUUID()),
          vars: { userId: session.user.id } // server-derived, never client-supplied
        }
      })
    }
  )

  // Flowise answers with plain JSON when the flow can't stream — same URL, same 200.
  const isSSE = upstream.headers.get('content-type')?.includes('text/event-stream')
  if (!upstream.ok || !isSSE || !upstream.body) {
    const body = await upstream.text()
    if (!upstream.ok) return new Response(body, { status: upstream.status })
    return new Response(JSON.parse(body).text ?? '', {
      headers: { 'Content-Type': 'text/plain; charset=utf-8' }
    })
  }

  return new Response(
    upstream.body
      .pipeThrough(new TextDecoderStream())
      .pipeThrough(flowiseTokens())
      .pipeThrough(new TextEncoderStream()),
    {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-store',
        'X-Accel-Buffering': 'no'
      }
    }
  )
}

// Flowise frames: "message:\ndata:{\"event\":\"token\",\"data\":\"Hi\"}\n\n"
function flowiseTokens() {
  let buf = ''
  return new TransformStream<string, string>({
    transform(chunk, controller) {
      buf += chunk
      const frames = buf.split('\n\n')
      buf = frames.pop() ?? '' // last element is an incomplete frame
      for (const frame of frames) {
        const line = frame.split('\n').find((l) => l.startsWith('data:'))
        if (!line) continue // ':heartbeat' comments and the bare 'message:' line
        let evt: { event: string; data: unknown }
        try {
          evt = JSON.parse(line.slice(5))
        } catch {
          continue
        }
        if (evt.event === 'token' && evt.data) controller.enqueue(String(evt.data))
        else if (evt.event === 'error') controller.error(new Error(String(evt.data)))
      }
    }
  })
}
```

`TextDecoderStream` / `TextEncoderStream` are stdlib on Node 18+ and Edge — they handle multi-byte characters split across chunks, which hand-rolled `TextDecoder` calls inside `transform` get wrong.

### Client component

```tsx
'use client'
import { useRef, useState } from 'react'

export function Chat() {
  const [answer, setAnswer] = useState('')
  const sessionId = useRef(crypto.randomUUID()) // one Flowise memory thread per mounted chat

  async function ask(question: string) {
    setAnswer('')
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, sessionId: sessionId.current })
    })
    if (!res.ok || !res.body) return setAnswer('Something went wrong.')

    const reader = res.body.pipeThrough(new TextDecoderStream()).getReader()
    for (;;) {
      const { done, value } = await reader.read()
      if (done) break
      setAnswer((a) => a + value)
    }
  }

  return (
    <>
      <p aria-live="polite">{answer}</p>
      <button onClick={() => ask('What should I read next?')}>Ask</button>
    </>
  )
}
```

Notes: `getReader()` rather than `for await (… of res.body)` — async iteration over `ReadableStream` still isn't universal in browsers, and this is two lines longer. Notice the client sends **no** `userId` — that's the point. `aria-live="polite"` so screen readers get the streamed text.

**Only tokens cross this boundary.** If you also need `sourceDocuments` or `metadata` in the UI, change the transform to enqueue `JSON.stringify(evt) + '\n'` and split on newlines client-side. Don't build that until you need it. If you're already on the AI SDK, keep this parsing loop and change only the `controller.enqueue` line to emit its stream protocol.

---

## 5. Symptom → cause

| Symptom | Cause |
|---|---|
| One JSON blob, no tokens | Flow not streamable. Check `GET /api/v1/chatflows-streaming/{id}`. Usually post-processing is enabled, or there's a Custom Function ending node. |
| Answer is generic, personalisation absent, no error | Override configuration not enabled in Settings → Configuration → Security, or `userId` not ticked, or the variable is `Static` instead of `Runtime`. |
| All tokens arrive at once at the end | A buffering hop. Flowise sets `X-Accel-Buffering: no`; set it on your response too, keep `dynamic = 'force-dynamic'`, and check for compression/proxy middleware in between. |
| Hangs, then 504 | Serverless timeout. Raise `maxDuration`. |
| `403` with a plain-text body | The chatflow's `allowedOrigins` rejected your `Origin` header. Note it's plain text, not JSON — a blind `res.json()` throws here. |
| `400 Invalid sessionId: must be a string` | You passed a number or object as `sessionId`. |
| `EventSource` won't connect | It can't — this is `POST` with an `Authorization` header. Use `fetch` + streams. |
| Every user shares one conversation | `sessionId` set to the user ID with no per-thread component. |
| Mangled characters mid-stream | Decoding chunks without a streaming decoder. Use `TextDecoderStream`. |

---

## 6. The lazier option: `flowise-sdk`

If you'd rather not own the frame parser, the official SDK yields already-parsed events:

```ts
import { FlowiseClient } from 'flowise-sdk'

const client = new FlowiseClient({
  baseUrl: process.env.FLOWISE_URL!,
  apiKey: process.env.FLOWISE_API_KEY
})

const prediction = await client.createPrediction({
  chatflowId: process.env.FLOWISE_CHATFLOW_ID!,
  question,
  streaming: true,
  overrideConfig: { sessionId, vars: { userId: session.user.id } }
})

for await (const chunk of prediction) {
  // chunk = { event: 'token', data: 'Hi' }
}
```

It replaces `flowiseTokens()` — about 12 lines — but you still write the bridge from that async generator into a `ReadableStream` for the browser, so the saving is smaller than it looks. Worth it if you're consuming several event types; not worth a dependency if you only want tokens.

---

## Sources

Verified against Flowise `main` rather than docs alone, because the wire format is the part the docs paraphrase:

- [`packages/server/src/utils/SSEStreamer.ts`](https://github.com/FlowiseAI/Flowise/blob/main/packages/server/src/utils/SSEStreamer.ts) — the `'message:\ndata:' + JSON.stringify(...) + '\n\n'` frame format, full event list, `:heartbeat`, `end`/`[DONE]`
- [`packages/server/src/controllers/predictions/index.ts`](https://github.com/FlowiseAI/Flowise/blob/main/packages/server/src/controllers/predictions/index.ts) — SSE headers, the `streaming` coercion, the silent `res.json()` fallback, `metadata` emitted last, `allowedOrigins` 403
- [`packages/server/src/services/chatflows/index.ts`](https://github.com/FlowiseAI/Flowise/blob/main/packages/server/src/services/chatflows/index.ts) — `checkIfChatflowIsValidForStreaming` eligibility rules
- [`packages/server/src/utils/index.ts`](https://github.com/FlowiseAI/Flowise/blob/main/packages/server/src/utils/index.ts) — `apiOverrideStatus` gate, per-variable override allowlist, `getMemorySessionId` precedence
- [Flowise docs: Streaming](https://docs.flowiseai.com/using-flowise/streaming) · [Prediction API](https://docs.flowiseai.com/api-reference/prediction) · [Variables](https://docs.flowiseai.com/using-flowise/variables)
