# Streaming a Flowise chatflow into a Next.js UI, with the user's ID attached

## The short version

One endpoint, `POST /api/v1/prediction/{chatflowId}` (singular — the docs contain a plural
`/predictions/` example that does not exist). Add `"streaming": true` and you get back
server-sent events whose `data:` lines each carry one JSON object of the shape
`{"event": "...", "data": ...}`. You render the `token` events and ignore the rest.

Two things that are worth getting right on the first pass rather than discovering later:

- **Mint the `chatId` yourself** and send it on the very first request. Otherwise you have to wait
  for the `metadata` event, which arrives *near the end of the answer*, before you can continue the
  conversation.
- **Pass the user through as both `sessionId` and `vars`.** They do different jobs, and if you send
  only `sessionId` it silently doubles as the `chatId` and merges all of that user's separate
  conversations into one stored thread.

Then the one that eats the most time: **`overrideConfig` is disabled by default**, per property,
so the userId you carefully pass will be dropped without an error until you enable it in the flow's
Security tab. Details in [Gotchas](#gotchas-in-rough-order-of-how-much-time-they-cost) below.

---

## 1. Look at the wire first

Before writing any code, run the request by hand. `-N` disables curl's output buffering, so you see
the events arrive at the speed the UI will see them.

```bash
curl -N -X POST https://flowise.example.com/api/v1/prediction/$FLOW_ID \
  -H "Authorization: Bearer $FLOWISE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "what should I read next?",
    "streaming": true,
    "chatId": "11111111-1111-1111-1111-111111111111",
    "overrideConfig": { "sessionId": "user-42", "vars": { "userId": "42" } }
  }'
```

This is also the fastest way to settle "is it my flow or my Next.js code?" — if the userId does not
reach the flow here, no amount of client work will fix it.

### What comes back

A stream of SSE frames, blank-line separated, each `data:` line holding one JSON object:

```
data:{"event":"start","data":""}

data:{"event":"token","data":"Based"}

data:{"event":"token","data":" on"}

data:{"event":"token","data":" what"}

data:{"event":"token","data":" you"}

data:{"event":"token","data":" read"}

data:{"event":"metadata","data":{"chatId":"11111111-1111-1111-1111-111111111111","chatMessageId":"9a2e…","question":"what should I read next?","sessionId":"user-42"}}

data:{"event":"end","data":"[DONE]"}
```

The event names and the `{event, data}` object shape are the contract — those are what the official
SDKs yield, so the same loop handles streaming and non-streaming responses. The purely cosmetic
parts (whether there is a space after `data:`, whether an SSE `event:` field accompanies the `data:`
line, the exact `end` payload) vary between versions and deployments, which is why the parser below
switches on the JSON object's own `event` field rather than the SSE frame's event type. Cheaper to
be tolerant than to pin a version to a byte layout.

### The full event set

| Event | When | Render it? |
|---|---|---|
| `start` | streaming begins | clear the message buffer |
| `token` | each token | **yes — this is your stream** |
| `metadata` | after all tokens, before `end`; carries `chatId` and message ids | not needed if you mint `chatId` |
| `sourceDocuments` | the flow returned vector-store sources | only if your UI shows citations |
| `usedTools` | the flow called tools | usually no — leaks internals |
| `error` | the prediction failed | yes, surface it |
| `end` | finished | re-enable the input |

Depending on the flow and its settings the stream can also carry `agentFlowEvent`, `nextAgentFlow`,
`calledTools` and similar. Those expose your node names and tool calls to anyone with devtools open,
which is why the route handler below filters rather than blindly piping.

For contrast, with `"streaming": false` you get one JSON body:
`{text, json?, question, chatId, chatMessageId, sessionId?, sourceDocuments?, usedTools?}`.

---

## 2. The request, from a Next.js route handler

Proxy it server-side. The API key must not reach the browser, and a Flowise flow is **public until
you attach a key** — anyone holding the chatflow id can call it.

```ts
// app/api/chat/route.ts
import { auth } from "@/lib/auth";          // your existing session helper
import { sseEvents } from "@/lib/flowise-sse";

// Events the browser is allowed to see. Everything else — agentFlowEvent,
// nextAgentFlow, calledTools, usedTools — describes your orchestration.
const CLIENT_EVENTS = new Set(["start", "token", "error", "end"]);

export async function POST(req: Request) {
  const session = await auth();
  if (!session?.user) return new Response("Unauthorized", { status: 401 });

  const { question, chatId } = await req.json();
  if (typeof question !== "string" || !question.trim()) {
    return new Response("question required", { status: 400 });
  }

  const upstream = await fetch(
    `${process.env.FLOWISE_URL}/api/v1/prediction/${process.env.FLOWISE_CHATFLOW_ID}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.FLOWISE_API_KEY}`,
      },
      body: JSON.stringify({
        question,
        streaming: true,
        chatId,                                    // client-minted UUID — see §4
        overrideConfig: {
          sessionId: session.user.id,              // scopes conversation memory
          vars: { userId: session.user.id },       // readable in prompts as {{ $vars.userId }}
        },
      }),
    },
  );

  if (!upstream.ok || !upstream.body) {
    return new Response("Upstream error", { status: 502 });
  }

  const enc = new TextEncoder();
  const filtered = new ReadableStream({
    async start(controller) {
      for await (const ev of sseEvents(upstream.body!)) {
        if (CLIENT_EVENTS.has(ev.event)) {
          controller.enqueue(enc.encode(`data:${JSON.stringify(ev)}\n\n`));
        }
      }
      controller.close();
    },
  });

  return new Response(filtered, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",   // no-transform stops proxies buffering
      Connection: "keep-alive",
    },
  });
}
```

Take `chatId` from the client rather than the request body if you prefer — the only requirement is
that it is stable for the life of one conversation. Never take `sessionId`/`userId` from the request
body: read them from the server-side session, or a user can personalise as somebody else.

If you do not care about the event leakage (internal tool, trusted users), the whole thing collapses
to `return new Response(upstream.body, { headers })` and you skip `sseEvents` on the server. That is
a real option — just make it a decision rather than an accident.

---

## 3. Reading it, token by token

One shared parser, used by both the route handler and the browser.

```ts
// lib/flowise-sse.ts
export type FlowiseEvent = { event: string; data: any };

/**
 * Parse an SSE byte stream into {event, data} objects.
 * Buffers across chunk boundaries: a network chunk can split a `data:` line
 * in half, and parsing per-chunk gives intermittent JSON errors under load.
 */
export async function* sseEvents(
  body: ReadableStream<Uint8Array>,
): AsyncGenerator<FlowiseEvent> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buf = "";

  for (;;) {
    const { value, done } = await reader.read();
    buf += done ? decoder.decode() : decoder.decode(value, { stream: true });

    for (let m; (m = /\r?\n\r?\n/.exec(buf)); ) {
      const frame = buf.slice(0, m.index);
      buf = buf.slice(m.index + m[0].length);
      const ev = parseFrame(frame);
      if (ev) yield ev;
    }

    if (done) return;
  }
}

/** SSE splits a payload containing newlines across several `data:` lines. */
export function parseFrame(frame: string): FlowiseEvent | null {
  const payload = frame
    .split(/\r?\n/)
    .filter((l) => l.startsWith("data:"))
    .map((l) => l.slice(5).replace(/^ /, ""))
    .join("\n");

  if (!payload || payload === "[DONE]") return null;
  try {
    const parsed = JSON.parse(payload);
    return typeof parsed?.event === "string" ? parsed : null;
  } catch {
    return null;                                // ignore keep-alives and comments
  }
}
```

```tsx
// components/use-flowise-chat.ts
"use client";
import { useRef, useState } from "react";
import { sseEvents } from "@/lib/flowise-sse";

export function useFlowiseChat() {
  const [answer, setAnswer] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // One id per conversation, decided here. Nothing waits on `metadata`.
  const chatId = useRef<string | null>(null);
  chatId.current ??= crypto.randomUUID();

  async function ask(question: string) {
    setAnswer("");
    setError(null);
    setStreaming(true);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, chatId: chatId.current }),
      });
      if (!res.ok || !res.body) throw new Error(await res.text());

      for await (const ev of sseEvents(res.body)) {
        if (ev.event === "token") setAnswer((a) => a + ev.data);
        else if (ev.event === "error") throw new Error(String(ev.data));
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "stream failed");
    } finally {
      setStreaming(false);                      // covers `end` and an aborted stream
    }
  }

  return { answer, streaming, error, ask, chatId: chatId.current };
}
```

Render `answer` directly — it grows per token, so the UI streams with no extra machinery.
`streaming` drives the disabled state on your input. Note `finally` rather than keying off the `end`
event: a dropped connection never sends `end`, and a UI stuck in "thinking" forever is the failure
mode that results.

**Do not reach for `EventSource`** — it is GET-only, so it cannot send the question. `fetch` plus a
reader is the correct primitive here, and needs no dependency.

### The one check worth keeping

The chunk-boundary buffering is the only non-obvious logic above, and it fails intermittently rather
than loudly, so it earns a test. Runs under `node --test` or vitest unchanged.

```ts
// lib/flowise-sse.test.ts
import test from "node:test";
import assert from "node:assert/strict";
import { sseEvents } from "./flowise-sse";

const stream = (...chunks: string[]) =>
  new ReadableStream<Uint8Array>({
    start(c) {
      for (const s of chunks) c.enqueue(new TextEncoder().encode(s));
      c.close();
    },
  });

const collect = async (s: ReadableStream<Uint8Array>) => {
  const out = [];
  for await (const ev of sseEvents(s)) out.push(ev);
  return out;
};

test("a frame split across chunks is not lost", async () => {
  // the boundary falls inside the word "token"
  assert.deepEqual(
    await collect(
      stream('data:{"event":"tok', 'en","data":"Hi"}\n\ndata:{"event":"end","data":""}\n\n'),
    ),
    [{ event: "token", data: "Hi" }, { event: "end", data: "" }],
  );
});

test("non-JSON frames are skipped, not thrown", async () => {
  assert.deepEqual(await collect(stream(":keep-alive\n\ndata:{\"event\":\"end\",\"data\":\"\"}\n\n")), [
    { event: "end", data: "" },
  ]);
});
```

---

## 4. Passing the user through: `sessionId` and `vars` do different jobs

Both go inside `overrideConfig`, and you generally want both.

| You send | The flow sees | Use it for |
|---|---|---|
| `sessionId: user.id` | the memory node's session key; `$flow.sessionId` in a Custom Function | scoping conversation memory to "this user's thread" |
| `vars: { userId: user.id }` | `{{ $vars.userId }}` in any text field; `$vars.userId` in code | **personalisation inside prompts** |

For prompt-level personalisation — "the user you are helping is `{{ $vars.userId }}`", or feeding it
to an HTTP node that fetches their profile — `vars` is the route you want.

Braces matter and the failure is quiet in both directions: `{{ $vars.userId }}` belongs in text
fields (prompts, URLs, headers, condition values), while inside a Custom Function's JavaScript body
you are in real code and it is bare `$vars.userId`. Braces in a function body are a syntax error;
the bare form in a prompt renders as literal text to the model.

If the id is only needed inside a Custom Function, `$flow.sessionId` already carries it and you can
skip the instance Variable entirely. Verify it first, though — `sessionId` is resolved from the
flow's memory node, so what `$flow.sessionId` holds depends on that node's configuration. `vars` is
the predictable route.

### Why send `chatId` as well

There is exactly one line in `buildChatflow.ts` that decides the chat id (verified on the `3.0.12`
tag, line 996):

```ts
const chatId = incomingInput.chatId ?? incomingInput.overrideConfig?.sessionId ?? uuidv4()
```

A caller-supplied `chatId` is used verbatim. Two consequences:

- **Drop `chatId` and your `sessionId` becomes the chat id.** Every conversation that user ever has
  shares one chat id, and their separate threads merge in the stored history. Sending both keeps
  "which user" and "which conversation" independent — which is what a real app wants.
- Because you already know the thread id, `metadata` becomes optional. Your send button can be live
  immediately instead of waiting for an event that arrives after the answer is nearly complete. It
  is also required to resume a paused human-in-the-loop execution, so owning it from the start pays
  off twice.

The docs use `chatId` in examples while omitting it from the schema. That is a documentation defect,
not a hint that it is optional.

---

## Gotchas, in rough order of how much time they cost

1. **`overrideConfig` is disabled by default** (since `2.1.4`), per property, in the flow's Security
   tab. This is the one that will hit you: an override that has no effect is almost always this, not
   a malformed body. Enable `sessionId` and `vars` explicitly for this flow. The **View API** button
   in the UI shows the authoritative list of overridable keys for a given flow — the docs publish no
   complete catalogue.
2. **`vars` can only override a Variable that already exists** on the instance. You cannot create
   `userId` through the API. Define it under Variables first, then override it per request.
3. **The path is singular.** `/api/v1/prediction/{id}`. The published docs contain a plural
   `/predictions/` example that does not exist.
4. **Array-typed `overrideConfig` properties concatenate, they do not replace.** If you expect a
   replacement you get both values.
5. **By default an override applies to every node of that type.** To target one node, nest by node
   id: `"llmMessages": { "llmAgentflow_0": [...] }`.
6. **`metadata` arrives near the end.** Design as if it will not arrive at all.
7. **Streaming has only been SSE since `2.1.0`.** An embed or client pinned below that will not
   receive messages from a newer server.
8. **In queue mode the stream is fed through Redis pub/sub**, which has a history of fragility —
   including a fix shipped and reverted in the same release. If tokens arrive in single-instance mode
   and stall in queue mode, start there rather than in your client code.
9. **`x-api-key` instead of `Bearer`.** Some deployments expose it, undocumented. Worth trying on an
   instance you do not control before concluding the key is wrong.

## Version note, because it changes what you should plan

**Flowise was archived upstream on 13 August 2026 and is read-only.** The core team leaves Discord
and GitHub on 31 August 2026, and vulnerability reports are no longer accepted.

**Pin `3.1.3`, not `3.1.4`.** The final release ships a Docker image reported not to boot on a fresh
volume (`EACCES` on `/root/.flowise`, missing `@smithy/eventstream-codec`, `this.db.exec is not a
function`). It will never be fixed. `3.1.3` (25 June 2026) is the last usable release.

The practical upshot for this integration: the wire format above is now permanently frozen, so the
parser you write today will not need revisiting. But nothing on the list above will be fixed either
— "file an issue and wait" is no longer an available move. Since you are building the boundary
between your app and the flow right now, keep it thin and keep an exported copy of the flow JSON in
your repo. That export is your specification if you ever reimplement, and there is no version
history in the product to recover it from.

Also worth knowing before anyone suggests forking: since `3.0.1` the repo is **dual-licensed**, not
plain Apache 2.0. `packages/server/src/enterprise/**` and `IdentityManager.ts` sit under a
FlowiseAI commercial licence, and `IdentityManager.ts` is load-bearing for auth and route mounting.
The README still says Apache 2.0; `LICENSE.md` is the operative document.
