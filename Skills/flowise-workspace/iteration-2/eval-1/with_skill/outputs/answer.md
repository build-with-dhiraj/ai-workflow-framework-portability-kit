# Support triage flow in Flowise: classify → conditionally call the invoice API → draft

Short version: build it as an **Agentflow V2** flow with **six nodes**. Classify with an **LLM node
using JSON Structured Output**, write the category into **Flow State**, branch with a **Condition
node** on the state key, put an **HTTP node** on the billing anchor, and give each branch its
**own** draft node. Do not merge the branches back together, and do not use an Agent node.

```
Start (Form Input: from_email, body)          declares state: category
  │                                            
  └─► LLM  "classify"                          JSON Structured Output → {category, reason}
        │                                      Update Flow State: category = {{ output.category }}
        └─► Condition  $flow.state.category == "billing"
              ├── anchor 0 (true) ─► HTTP  GET api.internal/invoices ─► LLM "draft (billing)"
              └── anchor 1 (ELSE) ───────────────────────────────────► LLM "draft (generic)"
```

---

## Read this before you build anything

Flowise was **archived on 13 August 2026**. It is read-only, the core team leaves Discord and
GitHub on 31 August 2026, and vulnerability reports are no longer accepted. Three things that
change *this* build:

- **Pin `3.1.3`, not `3.1.4`.** The final release ships a Docker image reported not to boot on a
  fresh volume (`EACCES` on `/root/.flowise`, missing `@smithy/eventstream-codec`, `this.db.exec
  is not a function`). It will never be fixed. `3.1.3` (25 June 2026) is the last usable release.
- **Every bug below is permanent.** "File an issue" and "wait for the fix" aren't moves any more,
  so each rough edge is something to design around, not report.
- **This flow will reach an internal API**, which means the instance sits next to your private
  network. Given six published RCE paths against `3.1.1`/`3.1.2` and public PoC code for an
  unauthenticated RCE and an SSRF, keep it off the public internet and behind auth. An
  internal-only instance is a much smaller problem.

None of that means don't build it. Classification + one HTTP call + a draft is a reasonable amount
of logic to keep in a graph, and being frozen means the behaviour won't move under you. But treat
it as a flow you'll eventually port rather than one you'll extend forever — the moment this grows a
fourth branch and a retry policy, it belongs in a service you own.

---

## The nodes, and why each one

| # | Node | Identifier | Job |
|---|---|---|---|
| 1 | Start | `startAgentflow` | Entry. Form Input. **Declares all Flow State keys** |
| 2 | LLM | `llmAgentflow` | Classify into the four categories, structured |
| 3 | Condition | `conditionAgentflow` | Deterministic branch on the category |
| 4 | HTTP | `httpAgentflow` | `GET https://api.internal/invoices?email=…` |
| 5 | LLM | `llmAgentflow` | Draft reply, billing path (sees the invoices) |
| 6 | LLM | `llmAgentflow` | Draft reply, everything else |

**Deliberately not used:**

- **No Agent node.** An Agent node reasons about *whether* to call the invoice tool. Your rule is
  "if billing, call it" — that's a rule, not a judgment, and an Agent will honour it most of the
  time, which is the worst reliability profile available. Reach for `agentAgentflow` when you
  genuinely want the model choosing tools.
- **No Tool node.** `toolAgentflow` runs one named tool deterministically, which would work, but
  you'd have to author a Custom Tool first. `httpAgentflow` is the direct fit for an outbound call.
- **No Condition Agent.** See "why not Condition Agent" below — there's a specific reason beyond
  taste.

---

## 1. Start node

Use **Form Input**, not chat input. The sender's address is already structured data on the inbound
email; do not hand a model a blob of text and ask it to find the address it can already read from a
header. Two fields:

| Field | Example |
|---|---|
| `from_email` | `jane@customer.com` |
| `body` | the email text |

Referenced downstream as `{{ $form.from_email }}` and `{{ $form.body }}`.

**Declare Flow State here, or nothing downstream works.** This is the single most common cause of
"my data disappeared" in Agentflow V2: every state key must be declared in the Start node's Flow
State parameter with an initial value, even an empty one. Nodes with an `Update Flow State` setting
can modify keys that already exist and **cannot create new ones** — a write to an undeclared key
silently does nothing and you get no error.

```json
[ { "key": "category", "value": "" } ]
```

That's the only key you need. (Reasoning below on why the HTTP result doesn't need one.)

## 2. LLM node — classify

Two settings carry this node.

**JSON Structured Output.** Declare the keys and types in the node's structured-output config
rather than writing "reply with JSON" in the prompt and hoping:

| Key | Type | Description you give the model |
|---|---|---|
| `category` | string | one of exactly: `billing`, `bug`, `feature-request`, `other` |
| `reason` | string | one short sentence, why |

`reason` is not decoration — it is the only thing that makes a misclassification debuggable after
the fact, and it costs you a handful of tokens.

**Prompt** — feed it the form fields:

```
Classify this support email into exactly one category.

billing         — invoices, charges, refunds, payment methods, plan pricing
bug             — something is broken or behaving incorrectly
feature-request — asking for something that does not exist yet
other           — anything else, including unclear or mixed intent

From: {{ $form.from_email }}
Body:
{{ $form.body }}
```

**Update Flow State** on this same node:

```json
[ { "key": "category", "value": "{{ output.category }}" } ]
```

Note `{{ output.… }}` — bare `output` is **self-referential** and only valid while configuring the
node that produces it. Anywhere else you reference a node by id: `{{ llmAgentflow_0.output.category }}`.
Mixing these up is the second most common Agentflow V2 mistake after the state declaration.

---

## 3. The branch — this is the part you asked about

**The mechanism, in order: structured output → Flow State → Condition on the state key.**

1. The LLM node emits `category` as a declared JSON field, so it's a value, not prose.
2. `Update Flow State` copies it into `$flow.state.category`.
3. The **Condition** node compares `{{ $flow.state.category }}` to the literal `billing`.

Condition node config:

| Setting | Value |
|---|---|
| Left value | `{{ $flow.state.category }}` |
| Operation | `Equal` |
| Right value | `billing` |

That yields **two output anchors** — one per outcome. `conditionAgentflow` gives you one anchor per
outcome, and each anchor is a real edge on the canvas you drag to a different node. Anchor 0 goes to
the HTTP node; the ELSE anchor goes straight to the generic draft node.

**Why the state key instead of branching on the model's response directly.** You *can* interpolate
`{{ llmAgentflow_0.output.category }}` into the condition — braces resolve in condition values the
same as in prompts. Use state anyway, for three reasons: the category is read by more than one node
(both drafts, plus anything you log), a state key survives you re-adding or reordering nodes whereas
a node-id reference does not, and `$flow.state` keys are how the next person reads your design —
listing a flow's state keys explains it faster than reading any prompt. Branching on raw model text
is the thing to actually avoid: it couples control flow to free text and the failures are
intermittent, which is the worst kind.

**Why not Condition Agent, specifically.** `conditionAgentAgentflow` does model-driven routing over
named scenarios, one anchor each, so it *looks* like it could replace nodes 2 and 3 and save you a
node. Don't, here — **Condition Agent cannot write Flow State.** The nodes that can update state are
LLM, Agent, Tool, HTTP, Retriever, Custom Function and Execute Flow. Route with a Condition Agent
and the category exists only as "which edge fired": nothing holds the value, so your draft prompts
and your reporting can't read it, and you'd end up hardcoding the category into each branch. The
general rule points the same way — prefer Condition whenever you can write the comparison, because
a deterministic branch you can read beats a model call, and one fewer model call is real latency.

**Two anchors, not four.** Your spec is "billing does one thing, everything else does the same
thing", so one comparison is all the flow needs. All four categories still land in state for the
draft prompt and your metrics. Split into four anchors when a second category actually needs
different handling.

**Put `billing` on the positive test.** If the model ever returns something outside your enum, the
ELSE anchor catches it and the email gets a generic draft. Test for `!= billing` instead and a
garbled classification sends a stranger's email address to your invoice API. Same node count, one
failure mode instead of the other.

---

## 4. HTTP node — the invoice call

| Setting | Value |
|---|---|
| Method | `GET` |
| URL | `https://api.internal/invoices?email={{ $form.from_email }}` |
| Headers | `Authorization: Bearer {{ $vars.invoiceApiToken }}` |

Braces interpolate in URLs and headers, not just prompts, so the email substitutes straight into the
query string. Store the token as an instance **Variable** and reference it as `$vars.invoiceApiToken`
rather than pasting it into the header literally.

**This node is where your build will break, and it is not your config.** `HTTP_SECURITY_CHECK`
became **on by default in `3.1.0`**, and its symptom is precisely "the HTTP node fails against
internal hostnames or `localhost`". `api.internal` is exactly that. Two ways out:

- **Curate `HTTP_DENY_LIST`** so your host is reachable while the guard stays on. Prefer this.
- **Disable the check**, knowing what you're switching off: it's an SSRF guard, on frozen software,
  with public PoC code for an SSRF that bypasses the cloud-metadata denylist. If you disable it,
  the network boundary around the container is now the only thing protecting your metadata endpoint.

Diagnose it by the symptom rather than assuming your URL is wrong — a working URL that a `curl` from
inside the same container resolves fine, failing only from the node, is this and not DNS.

**Reading the result.** The billing draft node is the only consumer and it sits immediately
downstream, so read the output directly in its prompt as `{{ httpAgentflow_0 }}` — no state key
needed. Add `Update Flow State` on the HTTP node only when a second node needs the same data.

Do check what the node actually returns before you write the prompt around it — whether you want
`{{ httpAgentflow_0 }}` or `{{ httpAgentflow_0.output.data }}` depends on your API's envelope, and
guessing here produces a draft that confidently references invoices it never received.

**One privacy note, since it's your API contract:** the customer's address travels in a query
string, so it lands in execution records and in anything logging URLs. Fine internally; worth a
thought if those logs travel.

## 5 & 6. Two draft nodes, and why you must not merge them

**Billing draft** (downstream of HTTP):

```
Draft a reply to this customer email. Category: {{ $flow.state.category }}.

Their invoices from our billing system:
{{ httpAgentflow_0 }}

Original email from {{ $form.from_email }}:
{{ $form.body }}

Reference specific invoice numbers, dates and amounts. If the data is empty or does
not answer their question, say a human will follow up — never invent an invoice.
```

**Generic draft** (on the ELSE anchor):

```
Draft a reply to this customer email. Category: {{ $flow.state.category }}.

Email from {{ $form.from_email }}:
{{ $form.body }}

Acknowledge the specific issue. Do not promise timelines or commit to shipping anything.
```

Yes, that's two prompts doing similar work, and normally you'd collapse them into one node that
both anchors point at. **Don't.** Conditions have a reported bug when two or more branches converge
on the same downstream node, and it will not be fixed. A branch that behaves inconsistently at a
merge point is the classic presentation. Two prompts you maintain beats an intermittent bug you
can't fix on software that will never be patched — and in practice the prompts diverge anyway,
because the billing one has to defend against an empty API response.

The last node on each path is that path's output, so the flow returns the draft either way. No
Direct Reply node needed unless you want a canned, no-model reply on some path.

---

## Calling it

```
POST /api/v1/prediction/{chatflowId}
Authorization: Bearer <api key>
```

```json
{
  "chatId": "<a UUID you generate>",
  "form": {
    "from_email": "jane@customer.com",
    "body": "I was charged twice for March…"
  }
}
```

Three things that catch people here:

- **`form`, not `question`.** `question` is required *unless* the flow uses Form Input, and yours
  does. Send the form field names as keys.
- **Mint `chatId` yourself and send it on the first request.** A caller-supplied `chatId` is used
  verbatim; the server only generates one when you omit it. Worth doing from day one because
  resuming a paused human-in-the-loop execution requires it, and because `chatId` otherwise only
  reaches you in the `metadata` SSE event, which arrives near the *end* of the stream.
- Note the path is singular, `/prediction/`. The docs contain a plural `/predictions/` example; that
  path does not exist.

If you inject anything through `overrideConfig` (say, per-call `vars`), remember it's been
**disabled by default since `2.1.4`, per property**, in the flow's Security tab. An override that
silently does nothing is nearly always that rather than a malformed body.

If you ever stream this to a non-internal UI, filter events server-side: the stream can carry
`agentFlowEvent`, `nextAgentFlow` and `calledTools`, which expose your node names and tool calls to
anyone with devtools open.

---

## What I left out, and when to add it

- **Human approval before send.** You said "draft", so I assumed a person reads it in your helpdesk.
  If you want the approve step *inside* Flowise, `humanInputAgentflow` pauses the run and gives you
  two anchors, proceed and reject. Add it when the approval has to be auditable in Flowise itself —
  and note resuming a paused execution needs that `chatId`.
- **Four anchors instead of two.** Add when a second category needs its own handling, not before.
- **A Custom Function anywhere.** Nothing here needs server-side JS. If you do add one later, two
  things bite: the function **must return a string** (returning an object is a classic
  runs-but-produces-nothing bug), and it must not write `$flow.state` directly as its main effect —
  return the value and let the node's own `Update Flow State` record it. Also, braces are for text
  fields only: `{{ $flow.state.category }}` inside a function body is a syntax error, and bare
  `$flow.state.category` inside a prompt renders as literal text to the model.
- **Splitting into sub-flows via `executeFlowAgentflow`.** Tempting when a flow grows, but flow state
  does *not* propagate into the child, and there's a reported defect where the node returns an
  identifier rather than the child's output — a silent data-loss bug one refactor later. If this
  outgrows one readable graph, move the orchestration into your own service instead.

**Node id suffixes depend on the order you add nodes** (`_0`, `_1`, … per type), so `httpAgentflow_0`
and `llmAgentflow_0` above are the ids you'll get if you build it in the order listed. Read the real
ids off the canvas before pasting interpolations — a wrong id renders as empty text, not as an error.
