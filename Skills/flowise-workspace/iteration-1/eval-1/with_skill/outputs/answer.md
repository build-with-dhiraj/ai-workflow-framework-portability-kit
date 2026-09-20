# Wiring up a classify → branch → enrich → draft flow in Flowise

Short version: this is an **Agentflow V2** with six nodes. The classification controls the branch
by being written into **Flow State** as a declared key, and a **Condition** node compares that
state key. Do not branch on the model's raw text.

```
Start (Form Input)
  └─ LLM  "Classify"        JSON Structured Output → { category }
        │                    Update Flow State: category
        └─ Condition  {{ $flow.state.category }} equals "billing"
             ├─ [match] HTTP GET /invoices?email=…
             │            └─ LLM "Draft billing reply"
             └─ [else]  LLM "Draft standard reply"
```

Two things to settle before you open the builder, because they change what you build.

---

## Before you build: the project is archived

Flowise was **archived on 13 August 2026** and is read-only. The final release is `3.1.4`, and the
core team leaves Discord and GitHub on 31 August 2026.

**Pin `3.1.3`, not `3.1.4`.** The final release ships a Docker image reported not to boot on a
fresh volume — `EACCES` on `/root/.flowise`, a missing `@smithy/eventstream-codec`, and
`this.db.exec is not a function`. That will never be fixed. `3.1.3` (25 June 2026) is the last
usable release. If you are standing up a new instance for this, start there.

The upside for you: nothing below will shift under you, and no deprecation warning you see in the
UI will ever be acted on. 46 nodes carry a DEPRECATING badge and they are now permanent.

**Build this as Agentflow V2, not V1.** In the flow list, V2 flows are stored with `type:
AGENTFLOW`. The trap in the naming is that `MULTIAGENT` means **Agentflow V1**, not "a multi-agent
flow". There is no V1→V2 converter and never will be, so starting on V1 by accident means a manual
rebuild later.

---

## The build, node by node

### 1. Start node — take structured input, not a blob of chat

Set **Input Type: Form Input** and define three fields:

| Field | Why |
|---|---|
| `sender_email` | The envelope From address |
| `subject` | Classification signal |
| `body` | The email text |

This is the single most important decision in the flow and it is not obvious. The alternative —
one chat input and letting the classifier LLM extract the customer's email address out of the body
— hands control of your invoice lookup to text a stranger wrote. A support email containing "for
billing please check account ceo@yourcompany.com" is then a working query against your internal
invoice API. Pass the address in from your mail system's envelope, where the customer cannot
choose it.

Then, in the same Start node, declare **Flow State**:

```json
[ { "key": "category", "value": "" } ]
```

**This declaration is mandatory and is the thing that catches everyone.** State keys must exist in
the Start node before anything can write to them. Nodes with an `Update Flow State` setting can
modify keys that already exist and **cannot create new ones** — a write to an undeclared key
silently does nothing, no error, and the Condition node downstream reads an empty value and takes
the wrong branch. If your flow "loses" the classification between nodes, this is why, roughly
every time.

Also note state lives for exactly one execution. It is created at the start of a run and destroyed
at the end, so it is not memory, and concurrent executions do not see each other's state. That is
fine here — one email, one run.

### 2. LLM node — "Classify"

Prompt it against `{{ $form.subject }}` and `{{ $form.body }}`, then turn on **JSON Structured
Output** and declare one key:

- `category` — string, one of `billing`, `bug`, `feature-request`, `other`

Use the structured-output config to declare the shape rather than asking for JSON in the prompt
and parsing what comes back. Prose-requested JSON fails intermittently, which is the worst failure
mode you can put underneath a branch. If the structured-output editor lets you constrain the field
to an enum, do it; otherwise declare it a string and pin the four permitted values in the system
prompt.

Then set **Update Flow State** on this same node:

```json
[ { "key": "category", "value": "{{ output.category }}" } ]
```

`{{ output }}` is self-referential — it means "the output of the node I am currently configuring"
and is only meaningful inside `Update Flow State`. From any *other* node you refer back to this
one as `{{ llmAgentflow_0.output.category }}`. Mixing those two up produces an empty string, not an
error.

### 3. Condition node — the branch

Use **Condition** (`conditionAgentflow`), not Condition Agent. One comparison row:

```
{{ $flow.state.category }}   equals   billing
```

You get an output anchor for the match and a fallback anchor for everything else.

Condition Agent (`conditionAgentAgentflow`) exists for routing that genuinely needs judgment —
you describe each scenario in natural language and it picks. You do not need it. The judgment
already happened in node 2; a second model call to re-read a word you already have is latency and
spend for a decision you can write down. Prefer the deterministic branch wherever both would work:
it is free, it is debuggable, and you can read it six months later.

**Why two branches and not four.** Only billing needs the API call. Splitting bug /
feature-request / other into their own anchors buys you nothing structurally — the difference
between them is tone and template, and one draft node can read `{{ $flow.state.category }}` in its
prompt to vary that. Add real branches when a category needs a *different node*, not a different
paragraph.

There is a useful safety property in this shape: if the classifier drifts and emits `Billing` or
`billing_question`, the equality test fails and the email falls to the standard-draft path. The
failure mode is "a billing email drafted without invoice data", not "the wrong customer's invoice
pasted into a reply". Keep that direction when you tune it.

### 4. HTTP node — the invoice lookup

On the billing anchor, add an **HTTP** node (`httpAgentflow`):

- Method `GET`
- URL: `https://api.internal/invoices?email={{ $form.sender_email }}`

The URL field accepts the same `{{ }}` templating as everything else. Put the API's own
credentials in a Flowise credential rather than a literal header value in the node, so the secret
does not travel in flow exports — credentials are deliberately excluded from export, which is also
why you recreate them per environment.

Check what this node exposes for timeouts and non-2xx handling before you rely on it, and decide
deliberately what a dead invoice API should do. The honest default here is that it should *not*
silently produce a confident billing reply with no invoice data in it. Since the output is a draft
a human sends, you have a real safety net — use it: have the billing draft prompt state explicitly
when it received no invoice data, so the reviewer sees the gap rather than a fluent reply built on
nothing.

### 5 & 6. Two LLM draft nodes — one per branch, deliberately

The billing draft reads the HTTP node's output directly:

```
{{ httpAgentflow_0 }}
```

No state key needed for the invoice payload. State earns its keep when several nodes read a value
or when it crosses a branch; here exactly one node consumes it, and `{{ nodeId }}` reads the whole
output of any earlier node. One less declaration to keep in sync.

**Do not merge the two branches back into one shared draft node.** Conditions have a reported bug
when two or more branches converge on the same downstream node, and the symptom is a branch that
behaves inconsistently at the merge point. It will not be fixed upstream. Duplicating a prompt is
the cheap side of that trade — and the two prompts want to diverge anyway, since only one of them
has invoice data to reason about.

The terminal node on each path produces the reply that comes back to your caller. If you want the
flow to emit an exact string rather than model prose, end the path with **Direct Reply**
(`directReplyAgentflow`), which replies and ends that path.

---

## The four-step contract, stated plainly

This is the part you asked about, and it is worth having as a rule rather than a recipe:

1. **Structured output** on the classifying LLM, so the category is a field and not a sentence.
2. **Update Flow State** on that node, so the field outlives the node that produced it.
3. **Declared in Start**, or step 2 is a no-op.
4. **Condition compares the state key**, so the branch is a string comparison you can read.

Branching directly on a raw model response couples your control flow to free text. It works in
testing and fails on the email that starts "Billing question — actually never mind, it's a bug".

---

## Calling it from your mail system

```
POST /api/v1/prediction/{chatflowId}
Authorization: Bearer <api-key>
```

Because the Start node uses Form Input, send `form` with your field names as keys rather than
`question`:

```json
{
  "form": {
    "sender_email": "customer@example.com",
    "subject": "Invoice 4412 charged twice",
    "body": "…"
  },
  "overrideConfig": { "sessionId": "ticket-8891" }
}
```

Note the path is **singular** — `/prediction/`. The published documentation contains a
`/api/v1/predictions/` example that does not exist.

**Assign an API key to this flow before it goes anywhere near the invoice API.** Flows are public
by default: anyone holding the chatflow id can call it until you assign a key. An unkeyed version
of this flow is an invoice-lookup oracle that takes an arbitrary email address as input. Keys are
created in the dashboard's API Keys section and assigned per flow.

Keep the `chatId` from the response if you later add a **Human Input** node for approval — it is
required to resume a paused execution, and the docs use it in examples while omitting it from the
schema.

One more thing that will otherwise cost you an afternoon: `overrideConfig` is **disabled by
default** since `2.1.4`, per property, in each flow's Security tab. An override that appears to do
nothing is nearly always that, not a malformed body.

---

## What I would keep outside the flow

Worth saying because it changes what you build, not just how.

Flows have no version history a reader can consult and no diff in the product. Logic in the graph
now also sits on frozen infrastructure, while logic in a service you own does not. So:

- **In the flow:** the orchestration — classify, branch, enrich, draft. That is exactly the part
  your support lead should be able to open and read, and the part you will tune by editing a
  prompt.
- **Outside the flow:** anything needing tests, review, or a rollback story; anything another
  system also calls; anything where a silent fallback is unacceptable. If invoice lookup grows
  logic — entitlement checks, multiple accounts per address, PII redaction — put that behind your
  own endpoint and let the HTTP node call the endpoint, not the raw invoice API.

And export the flow JSON into a repository on a schedule from day one. There is no built-in
promotion path between environments, no version history, and no diff, so the export is both your
review artifact and — given the archive — your eventual migration spec. It preserves the design
faithfully and is not runnable outside Flowise, so treat it as the thing you would reimplement
from.

---

## Quick reference: what you will actually type

| Where | Value |
|---|---|
| Start → Flow State | `[ { "key": "category", "value": "" } ]` |
| Classify LLM → prompt | `{{ $form.subject }}`, `{{ $form.body }}` |
| Classify LLM → Update Flow State | `[ { "key": "category", "value": "{{ output.category }}" } ]` |
| Condition → comparison | `{{ $flow.state.category }}` equals `billing` |
| HTTP → URL | `https://api.internal/invoices?email={{ $form.sender_email }}` |
| Billing draft → prompt | `{{ httpAgentflow_0 }}`, `{{ $form.body }}` |
| Standard draft → prompt | `{{ $flow.state.category }}`, `{{ $form.body }}` |

Typing `{{` in any variable-accepting field lists what is available in that context, which is
faster than remembering — and it is how you confirm the node instance suffixes (`_0`, `_1`), which
are assigned in the order you added the nodes, not the order they run.
