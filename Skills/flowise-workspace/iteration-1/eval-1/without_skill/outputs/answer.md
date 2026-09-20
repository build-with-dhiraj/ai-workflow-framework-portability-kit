# Support email triage in Flowise: classify → conditionally fetch invoices → draft

Short version: build it as an **Agentflow V2**, use an **LLM node with JSON structured output** to classify, an **HTTP node** for the invoice call, and a **Condition node** that reads the classifier's output to pick the branch. Six nodes total.

The thing you're actually asking about — "how do I get the classification result to control the branch" — comes down to two mechanics: **structured output** (so the classification is a *field*, not prose) and **variable interpolation** (`{{ nodeId.output.field }}` / `{{ $flow.state.key }}`), which is how the Condition node reads it.

---

## 1. Use Agentflow V2, not a Chatflow

Flowise gives you two canvases. Pick correctly, because retrofitting is painful:

- **Chatflow** — the classic LangChain-style canvas (chains, LLM, memory, vector stores). Branching here means a router/multi-prompt chain, which is awkward, opaque, and hard to debug.
- **Agentflow V2** — a graph canvas with real control-flow primitives: `Start`, `LLM`, `Agent`, `Tool`, `Condition`, `Condition Agent`, `HTTP`, `Custom Function`, `Loop`, `Iteration`, `Human Input`, `Direct Reply`, `Execute Flow`.

You want branching and an HTTP call on one branch only. That's Agentflow V2. New Agentflow → V2.

---

## 2. The shape

```
[Start]
  Input type: Form Input
  Fields: senderEmail, subject, body
  Flow State: category = ""   invoice = ""
     |
     v
[LLM: Classifier]
  JSON Structured Output -> category (enum: billing | bug | feature-request | other)
  Update Flow State: category = {{ llmAgentflow_0.output.category }}
     |
     v
[Condition]
  Row 0:  {{ $flow.state.category }}  Equal  "billing"
  Else:   everything else
     |
     |-- (0) billing --> [HTTP: GET invoices] --> Update Flow State: invoice = ...
     |                                                    |
     |                                                    v
     \-- (Else) ---------------------------------------> [LLM: Draft reply] --> [Direct Reply]
```

Both branches converge on **one** drafting LLM node. That's deliberate — see §6.

---

## 3. Node-by-node config

### Start node

Set **Input Type = Form Input** rather than Chat Input. An inbound support email isn't a chat turn; you have structured fields already (sender, subject, body) and you should not make an LLM re-derive them from raw text.

Define form fields:

| Label | Variable name | Type |
|---|---|---|
| Sender email | `senderEmail` | string |
| Subject | `subject` | string |
| Body | `body` | string |

Reference them anywhere downstream as `{{ $form.senderEmail }}`, `{{ $form.body }}`, etc.

Also on the Start node, open **Flow State** and declare two keys with empty defaults:

| Key | Default value |
|---|---|
| `category` | `""` |
| `invoice` | `""` |

Flow State is a per-run key/value store that any node can write to and every node can read via `{{ $flow.state.<key> }}`. Declaring the keys up front with `""` defaults is what makes the merge in §6 safe.

To fire the flow from your mail pipeline, POST to `/api/v1/prediction/<flow-id>`. Don't hand-write the payload — use the **API / Embed** button in the top-right of the canvas; it emits the exact request shape for the input type you configured, and the form-input payload shape has shifted across Flowise versions.

### LLM node — the classifier

Model: use a **small, cheap model** here (Haiku-class / gpt-4o-mini-class). Four-way topic classification does not need your drafting model. **Temperature 0.**

Messages / system prompt, roughly:

```
You classify inbound customer support emails into exactly one category.

billing         — invoices, charges, refunds, payment methods, subscriptions, pricing disputes
bug             — something is broken, erroring, or behaving incorrectly
feature-request — asking for something that does not exist yet
other           — anything else, including sales, spam, and unclear messages

Subject: {{ $form.subject }}
From: {{ $form.senderEmail }}

Body:
{{ $form.body }}
```

Then — **this is the important part** — open the **JSON Structured Output** section on the LLM node and add:

| Key | Type | Enum values | Description |
|---|---|---|---|
| `category` | `enum` | `billing, bug, feature-request, other` | The single best-fit category |

Use `enum`, not `string`. With `string` you are trusting prompt discipline and you will eventually get `"Billing"`, `"billing."`, or `"This appears to be billing"` — any of which silently fails an `Equal` comparison downstream and dumps the email into the wrong branch. With `enum` the value is constrained at the schema level and the comparison is safe.

Optionally add a second key `reason` (string) — costs almost nothing and makes misroutes diagnosable in the trace panel.

Finally, on the same node open **Update Flow State** and set:

| Key | Value |
|---|---|
| `category` | `{{ llmAgentflow_0.output.category }}` |

(Substitute the classifier's actual node ID. See §5 — use the variable picker, don't type it.)

### Condition node — the branch

Add a **Condition** node. Each row you add becomes a numbered output handle on the node; an **Else** handle is always appended at the end.

You only need **one row**:

| Type | Variable | Operation | Value |
|---|---|---|---|
| String | `{{ $flow.state.category }}` | `Equal` | `billing` |

Everything that isn't billing falls through to **Else**. Don't create four rows when three of them go to the same place — that's three extra edges to keep in sync for nothing.

Two behaviours to know:

- **First match wins.** The Condition node is if / else-if / else, not a fan-out. Exactly one output handle fires. That's what you want here, but it means row order matters the moment you add more rows.
- **Ordering.** If you later add per-category branches, put the most specific conditions first.

If you *do* later need four distinct drafting prompts, add rows for `bug` and `feature-request` and let `other` ride the Else. Don't do it now.

### HTTP node — the invoice lookup

On the **billing** (`0`) output handle, drop an **HTTP** node:

- **Method:** `GET`
- **URL:** `https://api.internal/invoices`
- **Query Params:** key `email`, value `{{ $form.senderEmail }}`

Put the email in the **Query Params** section rather than concatenating it into the URL string. The node URL-encodes params for you; a `+` in an email address (`dhiraj+support@…`) pasted into a raw URL becomes a space server-side and your lookup returns nothing.

**Auth:** don't paste a token into the header field. Either use the node's credential/authorization section, or create a Flowise **Variable** (Settings → Variables) and reference it as `{{ $vars.INVOICE_API_KEY }}` in an `Authorization` header. Variables can be sourced from the runtime environment, which keeps the secret out of the exported flow JSON — relevant because exported Agentflow JSON tends to get committed to git.

The response body is available downstream as `{{ httpAgentflow_0.output.data }}`.

Then, on the HTTP node's **Update Flow State**:

| Key | Value |
|---|---|
| `invoice` | `{{ httpAgentflow_0.output.data }}` |

### LLM node — the draft

Both branches point into this one node. Prompt:

```
You are drafting a reply for a human support agent to review and send.
Do not send. Do not promise refunds, credits, or dates.

Category: {{ $flow.state.category }}

Customer email:
{{ $form.body }}

Invoice data from our billing system (empty if not a billing enquiry — if empty,
do not reference invoices, amounts, or dates, and do not guess them):
{{ $flow.state.invoice }}
```

That last parenthetical is load-bearing. An LLM handed an empty variable will cheerfully invent an invoice number if you don't tell it not to.

Terminate with a **Direct Reply** node (or just let the drafting LLM be the terminal node — its output is what the API returns). Direct Reply is clearer if you later add branches that short-circuit.

---

## 4. The one-node alternative: Condition Agent

Flowise also has a **Condition Agent** node, which is an LLM that routes. You give it instructions plus a list of named scenarios, and each scenario becomes an output handle. It collapses your classifier LLM *and* your Condition node into one node.

Genuinely tempting, and if all you ever want is the branch, use it — it's half the nodes.

I'd still use the two-node version here, for one concrete reason: **Condition Agent doesn't leave you the label as data.** With LLM + structured output you have `category` sitting in flow state, so you can write it onto the helpdesk ticket, log it, count it, and eventually measure how often the classifier is wrong. With Condition Agent the decision happens inside the node and the only trace of it is which edge lit up. You will want that label within a month.

Use Condition Agent if the routing criteria are fuzzy and hard to express as a clean enum. Yours aren't.

---

## 5. Variable syntax — the actual mechanic

This is the part that trips people up. Flowise interpolates `{{ }}` inside almost any text field on any node.

| Reference | What it gets |
|---|---|
| `{{ $form.senderEmail }}` | A Start-node form field |
| `{{ question }}` | The chat input, if you used Chat Input instead of Form Input |
| `{{ llmAgentflow_0.output.content }}` | An upstream LLM node's raw text output |
| `{{ llmAgentflow_0.output.category }}` | A **key from that node's JSON Structured Output** — this is the one that matters |
| `{{ httpAgentflow_0.output.data }}` | An HTTP node's response body |
| `{{ $flow.state.category }}` | A flow-state key, readable from anywhere |
| `{{ $vars.INVOICE_API_KEY }}` | A global Flowise Variable |
| `{{ $flow.sessionId }}` | The run's session ID |

Node IDs follow the pattern `<nodeType>Agentflow_<n>` — `startAgentflow_0`, `llmAgentflow_0`, `conditionAgentflow_0`, `httpAgentflow_0`. **Don't type them from memory.** Text fields in Agentflow V2 have a variable picker (the `{}` button) that lists every reference actually available at that point in the graph. Use it — it's the difference between a working reference and a silently-empty string, and it also tells you immediately if you wired the edges wrong, because an unreachable upstream node won't appear in the list.

**Direct node reference vs. flow state.** You *can* write `{{ llmAgentflow_0.output.category }}` straight into the Condition node instead of `{{ $flow.state.category }}` — it works, one fewer thing to configure. I'd still route it through flow state, because (a) the drafting node needs the category anyway and one canonical read beats two different references to the same thing, and (b) flow-state keys have declared defaults, which is what makes the cross-branch merge in §6 predictable.

---

## 6. Merging the branches — why flow state, not a node reference

Your two branches converge on one drafting node. The billing branch ran the HTTP node; the other branch didn't.

If the drafting node referenced `{{ httpAgentflow_0.output.data }}` directly, that reference is to a node that **did not execute** on three of four paths. Best case it resolves to empty; either way you're relying on unspecified behaviour for a node that never ran.

Referencing `{{ $flow.state.invoice }}` is well-defined on every path: it's `""` because you declared it `""` on the Start node, unless the HTTP node overwrote it. One reference, always resolves, reads the same on both branches.

**Rule of thumb: anything read after a merge point should come from flow state, not from a node output reference that crosses a branch.**

---

## 7. Things that will bite you

**The HTTP node failing kills the run.** If `api.internal` is down or slow, the billing branch errors and you get *no draft at all* — for exactly the customers most likely to be angry. Decide now which you'd rather have: no reply, or a billing reply drafted without invoice data.

If it's the latter, replace the HTTP node with a **Custom Function** node that does the call in JS with a try/catch and returns `{}` on failure, writing the result to flow state. Custom Function nodes run arbitrary JS, can read `$flow.state` and node inputs, and can update flow state — so it's a drop-in swap. Roughly:

```js
try {
  const r = await fetch(
    `https://api.internal/invoices?email=${encodeURIComponent($form.senderEmail)}`,
    { headers: { Authorization: `Bearer ${$vars.INVOICE_API_KEY}` } }
  );
  return r.ok ? JSON.stringify(await r.json()) : "";
} catch (e) {
  return "";  // degrade to a draft without invoice data
}
```

Wire its return into flow state `invoice`. Keep the plain HTTP node if a hard failure is genuinely preferable to a partial draft — that's a support-policy call, not a technical one.

**`api.internal` must be resolvable from the Flowise container.** If you're running Flowise in Docker, an internal-only hostname on your corporate network will not resolve inside the container by default. Test the HTTP node in isolation before you build anything around it — this is the single most common reason "the flow works locally but not in staging."

**Don't put the customer's email in the URL string.** Covered above, but worth repeating: query params section, not string concatenation. Also — the sender's address is PII going to an internal endpoint over what had better be TLS. `https://` is correct in your spec; keep it.

**Classification cost.** Two LLM calls per email, but the classifier should be a cheap model. If you point both nodes at the same expensive model you've doubled your bill for no accuracy gain.

**Verifying the branch actually fires.** Agentflow V2 shows a per-run execution trace with each node's input and output. After a test run, open it and confirm: the classifier emitted `category: "billing"`, the Condition node lit handle `0`, and the HTTP node returned real data. If the branch always goes to Else, 90% of the time the cause is a string mismatch (`"Billing"` vs `"billing"`) — which is exactly what the enum in §3 prevents.

**Human review.** You said "draft," so presumably a person approves before send. If drafts land in your helpdesk as a draft/internal note, keep the approval there — don't build it into Flowise. If you actually want approval *inside* the flow, there's a **Human Input** node that pauses the run for approve/reject, but it makes the flow long-lived and stateful, which is a meaningfully bigger operational commitment. Default to the helpdesk.

---

## 8. Build order

1. Start node with form inputs + flow state → test with a hardcoded email, confirm `{{ $form.body }}` resolves.
2. Add the classifier LLM with the enum structured output → run 10 real emails, check `category` is right before building anything downstream.
3. Add the Condition node → confirm in the trace that the right handle fires.
4. Add the HTTP node **in isolation first** → prove `api.internal` is reachable and auth works.
5. Wire in the drafting LLM, converge both branches, add Direct Reply.

Get steps 2 and 4 correct independently. Almost every failure in this flow is one of those two, and debugging them through a fully-wired graph is much harder than debugging them alone.

---

**Skipped deliberately:** per-category drafting prompts (add rows to the Condition node when the prompts actually diverge), confidence-score routing to a human queue (add when you've measured the classifier's real error rate — you can't tune a threshold you haven't measured), retry/backoff on the invoice API (add if it proves flaky in practice; the try/catch degrade covers the common case).
