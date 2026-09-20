# Calling a Flowise chatflow from Next.js with token streaming + a user ID

## The short version

Three things:

1. **One endpoint.** `POST {FLOWISE_URL}/api/v1/prediction/{chatflowId}` with `"streaming": true` in the body. Same URL streaming or not — the flag and the chatflow's own config decide.
2. **On the wire you get SSE**, `Content-Type: text/event-stream`, framed as `message:\ndata:{...}\n\n`. Each `data:` line is a JSON envelope `{"event": "...", "data": ...}`. Text arrives as `event: "token"`. Everything else (metadata, source docs, tool calls) rides the same channel — you ignore what you don't want.
3. **The user ID goes in `overrideConfig.vars`**, and the flow reads it as `{{$vars.userId}}`. It does *not* go in the question string, and it must be read from your server session, never from the browser's request body.

The rest of this is the actual request, the actual bytes back, and the four things that will silently break it.

---

## 1. The request

```bash
curl -N -X POST https://flowise.example.com/api/v1/prediction/abc123-your-chatflow-id \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer REDACTED' \
  -d '{
    "question": "What should I read next?",
    "streaming": true,
    "chatId": "3f9c1e2a-...-conversation-uuid",
    "overrideConfig": {
      "vars": { "userId": "user_9f81" }
    }
  }'
```

Body fields that matter:

| Field | Purpose |
|---|---|
| `question` | The only required field. The user's message. |
| `streaming` | `true` asks for SSE. Only honoured if the chatflow also has streaming enabled — see gotcha 1. |
| `chatId` | Conversation identifier. **Pass your own** (a UUID you mint per conversation) and Flowise uses it as-is; omit it and Flowise mints one and tells you in the `metadata` event. Passing your own means you never have to parse metadata to keep a conversation going. |
| `overrideConfig.vars` | Runtime variables. This is your userId channel. |
| `overrideConfig.sessionId` | Optional. Keys the memory node. Defaults to `chatId`. |
| `history`, `uploads`, `form` | Also available; not needed here. |

`-N` on curl is important — without it curl buffers and you'll wrongly conclude streaming is broken.

---

## 2. What comes back on the wire

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

message:
data:{"event":"start","data":""}

message:
data:{"event":"token","data":"You"}

message:
data:{"event":"token","data":"'d"}

message:
data:{"event":"token","data":" probably"}

message:
data:{"event":"token","data":" enjoy"}

message:
data:{"event":"metadata","data":{"chatId":"3f9c1e2a-...","chatMessageId":"7b2d...","question":"What should I read next?","sessionId":"3f9c1e2a-...","memoryType":"Buffer Memory"}}

message:
data:{"event":"sourceDocuments","data":[{"pageContent":"...","metadata":{"source":"catalogue.pdf"}}]}

message:
data: [DONE]
```

Two things to notice about that framing:

- The bare `message:` line is a field with an empty value. A standard `EventSource` parser treats it as an unknown/ignorable field and still dispatches on the `data:` line as a default `message` event — so browser `EventSource` works, and so does a hand-rolled split-on-blank-line parser. (You can't use `EventSource` here anyway: it only does GET, and you need POST + an auth header. Use `fetch` + a reader.)
- The **payload** JSON has its own `event` key. That's the one you switch on, not the SSE event type.

### Event types you'll see

| `event` | `data` | What to do |
|---|---|---|
| `start` | `""` | Stream opened. Clear your buffer / drop the spinner. |
| `token` | string chunk | **This is the answer.** Append it. |
| `metadata` | object | Carries `chatId`, `chatMessageId`, `sessionId`. Useful if you didn't supply your own `chatId`. |
| `sourceDocuments` | array | RAG citations, if the flow retrieves. |
| `usedTools` / `calledTools` | array | Tool-call trace. |
| `agentReasoning`, `nextAgent`, `agentFlowEvent`, `nextAgentFlow` | varies | Agentflow progress. Tokens still arrive as `token`, so a token-only parser needs no changes. |
| `error` | string | Failure mid-stream. Surface it. |
| `[DONE]` (raw, not JSON) | — | Terminator sentinel. |

**Write the parser to ignore unknown `event` values.** The set grows between Flowise versions and new event types will appear in existing flows the day someone edits them in the UI.

### The non-streaming response (you will hit this)

If streaming isn't actually active, the same endpoint returns `application/json`, once, at the end:

```json
{
  "text": "You'd probably enjoy...",
  "question": "What should I read next?",
  "chatId": "3f9c1e2a-...",
  "chatMessageId": "7b2d...",
  "sessionId": "3f9c1e2a-...",
  "memoryType": "Buffer Memory",
  "sourceDocuments": [ ... ]
}
```

Same status code, same URL, completely different shape. Branch on the response `Content-Type`, not on what you asked for.

---

## 3. Next.js: the route handler

The Flowise API key must never reach the browser, so the route handler is a proxy. It also happens to be the right place to flatten Flowise's envelope into plain text, which keeps your React code from knowing anything about Flowise.

```ts
// app/api/chat/route.ts
import { auth } from '@/auth'

export const runtime = 'nodejs'
export const maxDuration = 60 // long RAG answers get guillotined at the default

export async function POST(req: Request) {
  const session = await auth()
  if (!session?.user?.id) return new Response('Unauthorized', { status: 401 })

  const { question, chatId } = await req.json()
  if (typeof question !== 'string' || !question.trim()) {
    return new Response('question required', { status: 400 })
  }

  const upstream = await fetch(
    `${process.env.FLOWISE_URL}/api/v1/prediction/${process.env.FLOWISE_CHATFLOW_ID}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.FLOWISE_API_KEY}`,
      },
      body: JSON.stringify({
        question,
        streaming: true,
        chatId,
        // userId comes from the server session — NEVER from the request body
        overrideConfig: { vars: { userId: session.user.id } },
      }),
    },
  )

  if (!upstream.ok || !upstream.body) {
    return new Response(await upstream.text(), { status: upstream.status || 502 })
  }

  // Streaming disabled on the chatflow → one JSON blob instead of SSE.
  if (!upstream.headers.get('content-type')?.includes('text/event-stream')) {
    const { text = '' } = await upstream.json()
    return new Response(text, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } })
  }

  return new Response(upstream.body.pipeThrough(flowiseTokens()), {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'no-store',
      'X-Accel-Buffering': 'no', // nginx in front of you will otherwise buffer the whole thing
    },
  })
}
```

### The transform: Flowise SSE → plain token text

```ts
// lib/flowise-stream.ts
export function flowiseTokens() {
  const dec = new TextDecoder()
  const enc = new TextEncoder()
  let buf = ''

  return new TransformStream<Uint8Array, Uint8Array>({
    transform(chunk, controller) {
      buf += dec.decode(chunk, { stream: true })
      let i: number
      // Frames are separated by a blank line. A chunk can split one mid-JSON,
      // so anything after the last \n\n stays in the buffer.
      while ((i = buf.indexOf('\n\n')) !== -1) {
        const frame = buf.slice(0, i)
        buf = buf.slice(i + 2)
        for (const line of frame.split('\n')) {
          if (!line.startsWith('data:')) continue
          const payload = line.slice(5).trim()
          if (!payload || payload === '[DONE]') continue
          let evt: { event?: string; data?: unknown }
          try {
            evt = JSON.parse(payload)
          } catch {
            continue
          }
          if (evt.event === 'token' && typeof evt.data === 'string') {
            controller.enqueue(enc.encode(evt.data))
          } else if (evt.event === 'error') {
            controller.error(new Error(String(evt.data)))
          }
          // every other event is deliberately dropped
        }
      }
    },
  })
}
```

If you also want the citations in the UI, don't extend this — send NDJSON instead of raw text (`controller.enqueue(enc.encode(JSON.stringify(evt) + '\n'))`) and let the client pick out what it renders. Same fifteen lines.

### The client

```tsx
'use client'
import { useRef, useState } from 'react'

export function Chat() {
  const [answer, setAnswer] = useState('')
  const [busy, setBusy] = useState(false)
  const chatId = useRef<string>(crypto.randomUUID()) // one conversation per mount

  async function ask(question: string) {
    setAnswer('')
    setBusy(true)
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, chatId: chatId.current }),
      })
      if (!res.ok || !res.body) throw new Error(await res.text())

      const reader = res.body.pipeThrough(new TextDecoderStream()).getReader()
      for (;;) {
        const { done, value } = await reader.read()
        if (done) break
        setAnswer((a) => a + value)
      }
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={(e) => { e.preventDefault();
      ask(new FormData(e.currentTarget).get('q') as string) }}>
      <input name="q" disabled={busy} />
      <p style={{ whiteSpace: 'pre-wrap' }}>{answer}</p>
    </form>
  )
}
```

That's the whole client. No dependency. If you already have Vercel's `ai` package installed you can feed these tokens into `useChat` via its data-stream protocol instead — but don't add it just for this. There's also an official `flowise-sdk` npm package that hides the SSE parsing behind an async iterator; it's fine, but it's another version to keep in step with your server for about twenty lines of saved code.

---

## 4. Getting the userId *into* the flow

Passing it in the request is half the job. In the Flowise UI:

1. **Variables** page → **Add Variable** → name `userId`, type **Runtime**. Type matters: a **Static** variable ignores whatever you send and always returns its stored value. This is the single most common reason personalisation "does nothing".
2. Reference it wherever you need it:
   - In a system prompt or Prompt Template: `{{$vars.userId}}`
   - In a Custom Tool / Custom Function JS body: `$vars.userId`
   - Alongside it you also get `$flow.chatId`, `$flow.sessionId`, `$flow.chatflowId`, `$flow.input`.

A typical personalising system prompt:

```
You are assisting user {{$vars.userId}}. Call the `get_user_profile` tool
with that id before answering anything preference-related.
```

Then the Custom Tool that actually fetches the profile does `fetch(`${API}/users/${$vars.userId}`)`.

**Memory scoping is a separate decision.** By default memory keys off `chatId`, i.e. per conversation — usually what a chat UI wants. If instead you want one rolling memory per user across all their conversations, add `"sessionId": session.user.id` to `overrideConfig`. Don't do both by accident: setting `sessionId` to the user id means two browser tabs share and interleave one history.

---

## 5. The four things that will silently break this

**1. Streaming isn't enabled on the chatflow.** Chatflow Configuration → the streaming toggle. And the *final* node in the flow has to support streaming — if your chain ends in something non-streaming (many output parsers, some chains, certain agent terminators), Flowise silently answers with the single JSON blob no matter what `"streaming": true` says. Status is still 200. This is why the route handler above branches on content type rather than trusting the flag.

**2. `overrideConfig` is rejected by default on recent Flowise.** Chatflow Configuration → **Security** → *Override Configuration*: enable it and allowlist the fields you're sending (`vars`, and `sessionId` if you use it). If you skip this, the request still returns 200 with a perfectly good generic answer — your userId is just dropped on the floor. Hardest failure in this whole integration to spot, because nothing errors.

**3. The API key leaking to the browser.** No `NEXT_PUBLIC_` prefix on `FLOWISE_API_KEY`, and no calling Flowise from a client component. The route handler is the trust boundary, which is also why `userId` is read from `auth()` there. If you accept `userId` from the POST body, any logged-in user can type someone else's id and read their personalised context.

**4. Buffering in front of you.** nginx buffers `text/event-stream` unless told not to (`X-Accel-Buffering: no`, set above; or `proxy_buffering off` in the site config). Cloudflare will buffer non-`text/event-stream` responses in some configurations — if plain text stalls, either switch the proxy response to `text/event-stream` too or check the CDN. And set `maxDuration` on serverless: the platform default will cut a long answer off mid-sentence, which looks exactly like a model bug.

Environment:

```
FLOWISE_URL=https://flowise.example.com
FLOWISE_CHATFLOW_ID=abc123-your-chatflow-id
FLOWISE_API_KEY=...
```

---

## 6. Verify it in two steps

**Step one — the wire.** Run the `curl -N` from section 1 before you write any TypeScript. If tokens dribble out one per line, streaming works and `overrideConfig` was accepted. If you get one JSON blob, it's gotcha 1 or 2 and no amount of client code will fix it. Ask the flow `"What is my user id?"` with a temporary `{{$vars.userId}}` echo in the system prompt to confirm the id actually landed.

**Step two — the parser.** The chunk-boundary handling is the only non-obvious logic here, so pin it:

```ts
// scripts/check-sse.ts — node --experimental-strip-types scripts/check-sse.ts
import { flowiseTokens } from '../lib/flowise-stream.ts'

const frames = [
  'message:\ndata:{"event":"start","data":""}\n\nmessage:\ndata:{"event":"tok',  // split mid-JSON
  'en","data":"Hel"}\n\nmessage:\ndata:{"event":"token","data":"lo"}\n\n',
  'message:\ndata:{"event":"metadata","data":{"chatId":"x"}}\n\ndata: [DONE]\n\n',
]

const ts = flowiseTokens()
const writer = ts.writable.getWriter()
const reader = ts.readable.getReader()
const enc = new TextEncoder()

const pump = (async () => {
  for (const f of frames) await writer.write(enc.encode(f))
  await writer.close()
})()

let got = ''
for (;;) {
  const { done, value } = await reader.read()
  if (done) break
  got += new TextDecoder().decode(value)
}
await pump

console.assert(got === 'Hello', `expected "Hello", got ${JSON.stringify(got)}`)
console.log('ok')
```

That fails loudly if a chunk boundary ever lands mid-JSON and you regress the buffering, and it proves `metadata` and `[DONE]` are dropped rather than concatenated into the answer.

---

One caveat worth stating plainly: the exact SSE framing (`message:` line, `[DONE]` sentinel) has shifted slightly across Flowise versions. The parser above is deliberately tolerant — it splits on blank lines, only reads `data:` lines, ignores unparseable payloads and unknown event types — so it survives those changes. But run the curl once against *your* instance and eyeball the bytes before you trust any of it.

**Skipped:** rendering source documents, tool-call traces, and abort/cancel. Add the first two by switching the transform to NDJSON (one line, noted above); add cancel by passing an `AbortSignal` into `fetch` on both sides when someone asks for a stop button.
