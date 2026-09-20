# Calling a Flowise chatflow from Next.js, streamed, with the user's ID attached

Short version: one `POST` to `/api/v1/prediction/{chatflowId}` with `"streaming": true`, proxied
through a route handler so the API key never reaches the browser. The user ID goes in
`overrideConfig` — via **two different keys** that do two different things. What comes back is
server-sent events whose `data:` payloads are JSON objects of the shape `{event, data}`.

There is one gotcha that will eat an afternoon if you don't know it, so it's first.

---

## Read this before you write the code: `overrideConfig` is off by default

Since Flowise `2.1.4`, **`overrideConfig` is disabled per-property** and has to be enabled in the
flow's **Security** tab in the UI. If you send `sessionId` and `vars` and the flow behaves exactly
as if you'd sent nothing, that is almost always this — not a malformed body, not a wrong key name.
The request still returns 200 and a perfectly good answer. It just quietly ignores you.

Two more rules that account for nearly all the remaining surprises:

- **`vars` can only override a variable that already exists.** You cannot create one through the
  API. Go to the dashboard's Variables section and create `userId` first, then `vars` overrides its
  value per request.
- **Array-typed config values concatenate, they don't replace.** Override an array property and you
  get the original plus yours. Rarely bites on `vars`, bites hard on things like message arrays.

The authoritative list of what's overridable for *your* flow is behind the **View API** button in
the flow's UI. The published docs don't carry a complete catalogue, so use the button, not the docs.

---

## The request

```
POST {FLOWISE_URL}/api/v1/prediction/{chatflowId}
Authorization: Bearer {api-key}
Content-Type: application/json
```

```json
{
  "question": "How do I reset my password?",
  "streaming": true,
  "chatId": "optional, to continue an existing conversation",
  "overrideConfig": {
    "sessionId": "conv_8f3a...",
    "vars": { "userId": "42" }
  }
}
```

`question` is required unless the flow uses a Form Input node, in which case you send `form` with
the form field names as keys instead. Files go in `uploads[]`, with `type` one of `audio`, `url`,
`file`, `file:rag`, `file:full`.

Note the path is **singular** — `/prediction/`. The official docs contain one example using
`/api/v1/predictions/` (plural). That path does not exist; every other reference is singular.

### Two ways to pass the user, and they are not interchangeable

| Key | What it does | Read inside the flow as |
|---|---|---|
| `overrideConfig.sessionId` | Scopes conversation **memory** — which prior turns this request can see | `$flow.sessionId` |
| `overrideConfig.vars.userId` | Injects a **value** the flow's prompts and nodes can interpolate | `{{ $vars.userId }}` / `$vars.userId` |

For personalisation — "address them by name", "only search their org's docs", "they're on the free
plan" — you want **`vars`**. That's the one your prompt templates and custom function nodes can
actually read.

`sessionId` is a separate decision about memory scoping, and the obvious choice is a trap worth
naming: if you set `sessionId` to the raw user ID, every conversation that user ever has collapses
into a single memory thread. That's fine for a persistent assistant and wrong for a product with a
"New chat" button. **Mint a conversation ID and use that as `sessionId`; pass the user ID through
`vars`.** They're different identities and conflating them is the usual cause of "why is it
remembering something from last week".

Inside the flow, a custom function node has access to `$vars.<name>`, `$flow.sessionId`,
`$flow.chatId`, `$flow.chatflowId`, `$flow.input`, and the whole `$flow.state` object — so once
`userId` is in `vars`, both prompt templates and code nodes can reach it.

---

## The Next.js route handler

Proxy it. Do not call Flowise from the browser: the API key would ship to the client, and
**Flowise flows are public by default** — anyone holding the chatflow ID can call it until a key is
assigned. Proxying also makes CORS a non-issue.

```ts
// app/api/chat/route.ts
import { auth } from "@/lib/auth"; // whatever gives you the logged-in user

export const runtime = "nodejs";

export async function POST(req: Request) {
  const session = await auth();
  if (!session?.user) return new Response("Unauthorized", { status: 401 });

  const { question, conversationId, chatId } = await req.json();

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
        ...(chatId && { chatId }),
        overrideConfig: {
          sessionId: conversationId,          // memory scope
          vars: { userId: session.user.id },  // personalisation — from the SESSION, never the body
        },
      }),
    }
  );

  if (!upstream.ok || !upstream.body) {
    return new Response(await upstream.text(), { status: upstream.status });
  }

  return new Response(upstream.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no", // stops nginx buffering the stream into one lump
    },
  });
}
```

`upstream.body` is a `ReadableStream`, so returning it directly pipes Flowise's bytes straight
through with no parsing on the server. That's the whole proxy.

**The user ID comes off the server session, never off the request body.** If the client supplies it,
your personalisation is spoofable by anyone who opens devtools — they type someone else's ID and the
flow personalises for that person. The `conversationId` is fine to take from the client (it only
scopes memory), but bind it to the user if conversations are private.

If `Authorization: Bearer` returns 401 or 403 against an instance you don't control, try
`x-api-key` before concluding the key is wrong — some deployments use it, and it's undocumented.

---

## What you actually get back on the wire

With `"streaming": true`, `Content-Type: text/event-stream` and a sequence of SSE frames. The
`data:` payload of each frame is a JSON object shaped `{ "event": "...", "data": ... }` — which is
also the shape the official SDKs yield, so the same loop handles both.

```
data: {"event":"start","data":""}

data: {"event":"token","data":"To"}

data: {"event":"token","data":" reset"}

data: {"event":"token","data":" your password"}

data: {"event":"metadata","data":{"chatId":"...","chatMessageId":"...","sessionId":"..."}}

data: {"event":"end","data":"[DONE]"}
```

The full event set:

| Event | When |
|---|---|
| `start` | streaming begins |
| `token` | each token — this is the one you append to the UI |
| `metadata` | after all tokens, before `end`; carries `chatId` and message IDs |
| `sourceDocuments` | the flow returned vector-store sources |
| `usedTools` | the flow called tools |
| `error` | the prediction failed |
| `end` | finished |

**The ordering has a real UI consequence: `metadata` arrives near the *end*, not the start.** So
`chatId` is not available when the first token lands. If the user closes the tab mid-stream you
never receive it at all. This is exactly why you should mint your own conversation ID and send it as
`sessionId` — you then have a stable handle from request #1 and don't need to wait on `metadata` to
know which thread you're in. Keep `chatId` when it arrives anyway: it's how the server continues a
conversation, and it's **required** to resume a paused human-in-the-loop execution. (The docs use
`chatId` throughout their examples while omitting it from the published schema — that's a doc defect,
not a hint that it's optional.)

Handle `error` explicitly. It arrives as an event inside a 200 response, so a naive "did the fetch
succeed" check will report a failed prediction as a success.

### For comparison, the non-streaming response

Drop `streaming` (or set it false) and you get one JSON object:

```json
{ "text": "...", "json": {}, "question": "...", "chatId": "...",
  "chatMessageId": "...", "sessionId": "...", "sourceDocuments": [], "usedTools": [] }
```

### Look at your own instance before you trust any of this

`streaming: true` is a request, not a guarantee — check what your flow actually emits:

```bash
curl -N -X POST "$FLOWISE_URL/api/v1/prediction/$CHATFLOW_ID" \
  -H "Authorization: Bearer $FLOWISE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question":"hello","streaming":true}'
```

`-N` disables curl's buffering so you see frames as they arrive. If you get one JSON blob instead of
a stream, check the response `Content-Type` — that tells you whether the server opened a stream at
all, and saves you debugging client parsing code against a non-stream.

---

## Consuming it in the client

`EventSource` is GET-only, so it can't be used here. Either hand-roll the reader (below, ~25 lines,
no dependency) or pull in `@microsoft/fetch-event-source` if you want automatic reconnect.

```ts
"use client";
import { useState } from "react";

export function useFlowiseChat(conversationId: string) {
  const [answer, setAnswer] = useState("");
  const [chatId, setChatId] = useState<string>();

  async function ask(question: string) {
    setAnswer("");
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, conversationId, chatId }),
    });
    if (!res.ok || !res.body) throw new Error(await res.text());

    const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
    let buf = "";

    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += value.replace(/\r\n/g, "\n"); // SSE permits CRLF

      const frames = buf.split("\n\n");
      buf = frames.pop() ?? ""; // keep the trailing partial frame

      for (const frame of frames) {
        const payload = frame
          .split("\n")
          .filter((l) => l.startsWith("data:"))
          .map((l) => l.slice(5).trim())
          .join("\n");
        if (!payload || payload === "[DONE]") continue;

        let msg: { event: string; data: any };
        try { msg = JSON.parse(payload); } catch { continue; }

        if (msg.event === "token") setAnswer((a) => a + msg.data);
        else if (msg.event === "metadata") setChatId(msg.data?.chatId);
        else if (msg.event === "error") throw new Error(String(msg.data));
      }
    }
  }

  return { answer, chatId, ask };
}
```

Two details in there that matter and are easy to get wrong:

- **Buffer across chunks.** A network chunk can split a frame in half. `frames.pop()` keeps the
  trailing partial for the next read — without it you drop or corrupt tokens under load, and it only
  shows up intermittently in production.
- **Switch on the JSON payload's `event` field**, not on the SSE `event:` line. The JSON carries the
  type either way, so this parses correctly regardless of how your server version frames it.

Skipped: token batching. Every token triggers a re-render — add a `requestAnimationFrame` buffer only
if you see jank on long answers.

If you're already using the Vercel AI SDK's `useChat`, don't expect Flowise's frames to line up with
it by accident. Translate `{event, data}` into that hook's expected protocol inside the route handler
rather than fighting it on the client.

---

## Operational caveats worth knowing up front

**The project is archived.** Flowise was archived upstream on 13 August 2026 and is read-only. The
core team leaves Discord and GitHub on 31 August 2026, and vulnerability reports are no longer
accepted. Nothing below gets fixed, so plan around it rather than filing issues.

- **Pin `3.1.3`, not `3.1.4`.** The final release (`3.1.4`) ships a Docker image reported not to boot
  on a fresh volume — `EACCES` on `/root/.flowise`, a missing `@smithy/eventstream-codec`,
  `this.db.exec is not a function`. It will never be fixed. `3.1.3` (25 June 2026) is the last usable
  release.
- **Streaming needs `>= 2.1.0`.** SSE replaced the older transport there. Anything pinned below that
  — notably an old embed widget — will not receive messages from a newer server.
- **Queue mode makes streaming more fragile.** With `MODE=queue`, the stream is fed through Redis
  pub/sub, which has a history of problems including a fix that shipped and was reverted in the same
  release. If streaming works on a single node and breaks in your clustered environment, look there
  first — it's the environment, not your client code.
- Since the archive, the export JSON is your migration artifact as well as your backup. Commit each
  flow's export to a repo on a schedule — there is no version history, no diff and no promotion path
  in the product, and the export is the specification you'd reimplement from if you ever move off.

---

## Checklist

1. Create a `userId` **Variable** in the Flowise dashboard.
2. In the flow's **Security** tab, enable overrides for `vars` and `sessionId`.
3. Reference it in your prompts as `{{ $vars.userId }}`.
4. Assign an API key to the flow (it's public until you do).
5. Confirm the wire format with the `curl -N` above.
6. Then wire the route handler and the client hook.

Steps 1, 2 and 4 are the ones people skip, and skipping 2 fails silently with a 200.
