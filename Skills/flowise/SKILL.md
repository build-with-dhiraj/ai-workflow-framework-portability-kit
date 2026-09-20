---
name: flowise
description: Expert working knowledge of Flowise, the open-source LLM and agent builder (chatflows, agentflows, custom function nodes, the prediction API, self-hosting). Use this whenever Flowise is mentioned, or when the user is reading, auditing, building, debugging, deploying or calling a flow, including when they only name a flow or a node and never say "Flowise". Use it when someone asks why an AI feature returns irrelevant results and that feature is built on a flow, or asks how one working flow differs from another that is not working. Use it before answering anything about Flowise versions, upgrades or self-hosting, because the project was archived upstream on 13 August 2026 and version guidance recalled from memory is now wrong.
---

# Flowise

Flowise is a visual builder for LLM applications. Flows are stored as a node graph and
executed server-side, so the product's real behaviour lives in a graph rather than in a repo,
and reading that graph is a genuine skill rather than an inconvenience.

## Lead with this, it changes most answers

**The project was archived on 13 August 2026 and is read-only.** The final release is `3.1.4`
(29 July 2026). The core team leaves Discord and GitHub on 31 August 2026, and the security
policy was replaced with a notice that vulnerability reports are no longer accepted.

Three consequences worth stating before giving anyone advice:

- **Pin `3.1.3`, not `3.1.4`.** The final release ships a Docker image reported not to boot on
  a fresh volume (`EACCES` on `/root/.flowise`, missing `@smithy/eventstream-codec`,
  `this.db.exec is not a function`). It will never be fixed. `3.1.3` (25 June 2026) is the last
  usable release.
- **"Just fork it, it's Apache 2.0" is not accurate.** Since `3.0.1` the repo is dual-licensed:
  `packages/server/src/enterprise/**` and `IdentityManager.ts` sit under a FlowiseAI commercial
  licence. `IdentityManager.ts` is load-bearing for auth and route mounting, so a fork intended
  to carry auth needs that resolved first. The README still says plain Apache 2.0; `LICENSE.md`
  is the operative document.
- **Nothing marked "will be removed in a future release" ever will be.** 46 nodes carry a
  DEPRECATING badge, including the whole LlamaIndex integration and the legacy agents. They are
  now permanent. That cuts both ways: no forced migration, and no fixes either.

Being frozen has one upside worth using: the facts below stop moving, so they can be stated
precisely rather than hedged.

## Work out which question you are answering

| The user wants to | Read |
|---|---|
| Understand what an existing flow actually does, or extract its prompts and logic | `references/audit.md` |
| Work out why flow A works and flow B does not, and what to copy | `references/transfer.md` |
| Design or modify a flow: node choice, branching, state, structured output | `references/agentflow-v2.md` |
| Call a flow from code, stream it, embed it, or move it between environments | `references/api.md` |
| Deploy, upgrade, scale, secure, or diagnose an instance | `references/operate.md` |

Read the one that fits. They are written to stand alone, so pulling in all five wastes context.

## Reach for the client before writing throwaway code

`scripts/flowise.mjs` is a dependency-free Node client for reading an instance. Use it rather
than curling the API by hand, because it already absorbs the three encodings that sit between
you and the meaning of a flow.

```bash
export FLOWISE_API_ENDPOINT=https://flowise.example.com FLOWISE_API_KEY=...

node scripts/flowise.mjs flows                  # every flow: type, node count, id
node scripts/flowise.mjs nodes   "My Flow"      # node map with kinds, sizes, edges
node scripts/flowise.mjs vars    "My Flow"      # every {{ }} reference, per node
node scripts/flowise.mjs prompts "My Flow"      # all prompts, HTML decoded
node scripts/flowise.mjs code    "My Flow" --node "Search"   # JS body + its inputs
node scripts/flowise.mjs flow    "My Flow" --out flow.json   # whole flow
node scripts/flowise.mjs get     /api/v1/nodes  # any endpoint, raw
node scripts/flowise.mjs diff    a.json b.json  # semantic diff, ignoring ids and canvas positions
```

Credentials come from `--endpoint`/`--key`, then the environment, then `~/.flowise.json`.
Flow lookup accepts an id, an exact name, or a case-insensitive substring.

`diff` is built for the question "has production drifted from the flow I read on dev?" The same
flow on two instances has different node ids, credential ids and canvas coordinates, so a naive
comparison marks every node changed and answers nothing. This one normalises those away, compares
each node's inputs, and names the fields that actually moved. "No semantic differences" is a real
answer you can act on.

`vars` is the underrated one. A flow's state keys are named by whoever understood the problem,
so listing them and which nodes touch them explains the design faster than reading any prompt.

## Five facts that decide most answers

**Flows are one table, discriminated by `type`.** `CHATFLOW`, `AGENTFLOW`, `MULTIAGENT`,
`ASSISTANT`. The trap: **`MULTIAGENT` means Agentflow V1**, not "a multi-agent flow". Agentflow
V2 is `AGENTFLOW`. Filter with `/api/v1/chatflows?type=AGENTFLOW`.

**`flowData` is a JSON string inside the flow object.** Parse it or the flow looks empty. This
is the single most common reason a first attempt returns nothing.

**There is no `/api/v1/agentflows` endpoint.** That path returns the single-page app's HTML with
a 200, which looks like a working response and is not. Agentflows come from the chatflows route
with a type filter. The bundled client detects this and says so.

**`$flow.state` keys must be declared in the Start node.** Operational nodes can update existing
keys but cannot create new ones, and state lives for exactly one execution. A flow that seems to
lose data between nodes is usually missing a declaration, not misusing the syntax.

**`overrideConfig` is disabled by default** since `2.1.4`, per property, in the flow's Security
tab. An override that silently does nothing is nearly always this rather than a malformed body.

## How to be useful here

**Read the graph before believing the description.** The person who built a flow will describe
what they intended, accurately as they remember it, and be wrong in specific ways that cost real
time. Flows are edited in a GUI with no version history a reader can consult, so the graph is
the only account that is current. This matters most when someone asks you to copy what another
flow does: verify the mechanism, then ask the human for the reasoning, which is the part the
graph genuinely does not hold.

**Prefer citing a node to asserting a behaviour.** "Node 4 reduces each candidate to id, title
and type before curation" is checkable. "The flow only passes titles" is an opinion until it
names where. Analyses from this work usually end up in front of people making scheduling
decisions, so they need to survive someone opening the flow.

**Distinguish what is broken from what is unfixable.** Since the archive, "file an issue" and
"wait for the fix" are no longer available moves. When you hit a known bug, say whether a
workaround exists, whether pinning an earlier version avoids it, and that upstream will not
resolve it. That changes what the user should plan, which is the actual question behind most
bug reports.

**Say when the docs are wrong.** The published documentation contains real defects: a plural
`/predictions/` path that does not exist, a Docker example carrying another product's port and
an invalid `DATABASE_TYPE`, a `Chatflow.type` enum missing `AGENTFLOW` entirely, and a
`WORKER_CONCURRENCY` default of 10000 that is a copy error. `references/operate.md` and
`references/api.md` list these. Repeating a doc defect confidently is worse than saying you are
unsure.
