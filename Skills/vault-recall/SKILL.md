---
name: vault-recall
description: The second brain over the JoVE HQ vault at ~/dev/jove-hq/knowledge, and no other source. Recalls, cross-links, and grills - answers "what did we decide / who owns / did we ever / what's still open", traces how notes connect, and interviews Dhiraj against what the vault actually says. Read everything, rank nothing; cite or abstain. Use for any recall, decision, ownership, history, or grilling question, or on "recall", "what did we decide", "did we ever", "what's our position on", "grill me on", /vault-recall, /jove-recall.
---

> **Project root:** every relative path here resolves against `~/dev/jove-hq`, never the cwd. Invocable from anywhere; prefix accordingly.

# Vault recall (read everything, rank nothing)

The second brain over `~/dev/jove-hq/knowledge`. Three jobs, one source: **recall** what is
written down, **cross-link** how it connects, **grill** Dhiraj against it.

## Scope: one vault, nothing else

Answers come from `~/dev/jove-hq/knowledge` and nowhere else. Not other vaults
(`~/mentors/vault`, `~/invest/vault`, `~/dev/connecting-dots/vault`, iCloud), not the open web,
not model recall. Routes 4 and 5 below name Linear and live sources - those are **hand-offs**,
signposts saying "this is not a vault question", never a second source to answer from.

Never use this skill for live data (today's calendar, unread Slack, open Jira). Recall answers
what is *written down*, not what is *happening now*. Corollary: **the ledger is only as fresh as
the last sweep write-back.** For something decided earlier *today*, check the day's call
transcripts before trusting a ledger abstention - verified 20 Aug 2026, when the ledger answered
"no committed timeline" hours after a call had set one.

## Why this design and not vector RAG

Every recall failure this project has had came from ranking, not from retrieval: a stale GTM doc
beat the verified 90-day trial answer at 0.892 cosine; a superseded draft marked "Status: Open"
outranked the ledger entry recording the fix. Top-k cannot crowd out the truth if nothing is
ranking. The ledger is ~67k tokens against a 1M+ window; the whole corpus is a few percent of one
call. Recall is 100% by construction and the model's job is judgment, not search. **Do not
"improve" this with embeddings.**

## Route the question

**1. Any JoVE Labs question** - decisions, bugs, scope, tickets, launch state:

```bash
node ~/dev/jove-hq/tools/sweep/ledger-ask.mjs "the question"
```

Add `--open` when the question is "what is blocking / what's still open". The answer arrives cited
to F-### findings with verbatim quotes; stderr prints call/token/latency stats (informational, not
part of the answer).

**2. Ledger abstains, or the question needs primary sources** (what someone actually said, a call,
a doc):

```bash
node ~/dev/jove-hq/tools/sweep/ledger-ask.mjs --corpus "the question"
```

Additionally reads ALL of `knowledge/jove-labs/` and `knowledge/meetings/` (widened 21 Aug 2026) (~347 notes, 1.29M tokens) in parallel shards and
unions verbatim hits with file paths. Exhaustive, not probabilistic. Costs wall-clock, not money
worth counting. **Scope caveat: `--corpus` covers `knowledge/jove-labs/` only** - for the rest of
the vault, route 3.

**3. Non-Labs vault questions** (PPP, personas, meetings outside Labs, strategy):

- Start at `knowledge/HOME.md`, the hand-owned front door - every area one hop away.
- **Only `jove-labs/` has a generated `INDEX.md`.** Other folders do not; do not go looking for one.
  Their entry point is HOME plus the `moc:` layer under Cross-linking below.
- Then lexical: `rg -il --hidden` over `~/dev/jove-hq/knowledge/`, and **read the hit files whole**, not
  snippets. A decision's reversal is often three lines below the match.
- Exclude `youtube-academia-corpus/` unless it is genuinely the target: it is 8,718 of the vault's
  ~11,200 notes and is scraped corpus, not notes.

**4. Structure questions** (what's stale, what's disputed, what's unowned): the Obsidian `.base`
tables, regenerated at sweep write-back, not free-text search:
`jove-labs/ops-this-week.base`, `ops-stale.base`, `ops-assumed.base`, `ops-contradictions.base`,
`ops-unowned.base`, `ops-by-surface.base`, `findings/findings.base`.

**5. Hand-offs, not answers.** Work-state ("what's open / where did we leave off") lives in the
Linear project "JoVE HQ - Continuation & Ops". Metrics and numbers: `knowledge/memory/stakeholder-artifacts.md`
first, then the named artifact, then reconcile with the live source; drift is the finding. Say
where the answer lives; do not present the live system's contents as vault recall.

## Cross-linking

How notes connect is itself an answer. The link layer is verified present, not assumed.

- **Hubs.** `HOME.md` is the spine. `jove-labs/moc/_map.md` maps 45 topic MOCs. `jove-labs/decisions/_index.md`
  holds one settled decision per note with verbatim evidence, and **outranks a passing mention
  anywhere else** - check it before treating something as open. `jove-labs/findings/_index.md` is
  the findings ledger.
- **Hub membership** via frontmatter (609 notes carry `moc:`):

```bash
grep -rl '^moc: .*jove-labs' ~/dev/jove-hq/knowledge --include="*.md"
```

- **Backlinks.** Links come in bare `[[note]]` (~42,900 uses) and piped `[[path/note|Display]]`
  (~1,900). A bare-form grep silently undercounts - verified 65 vs 72 notes for `jove-labs`:

```bash
# WRONG - misses every piped link
grep -rl "\[\[jove-labs\]\]" ~/dev/jove-hq/knowledge --include="*.md"

# RIGHT - matches both forms
grep -rlE "\[\[[^]]*jove-labs[]|]" ~/dev/jove-hq/knowledge --include="*.md"
```

- **Filenames carry meaning.** kebab-case, `-YYYY-MM-DD` suffix on anything time-bound, and a
  SCREAMING prefix marking kind in `jove-labs/`: `HANDOVER-`, `ANSWER-`, `METRICS-`, `TICKET-DRAFT-`,
  `OUTBOX-`, `TODAY-PLAN-`, `CROSS-ACCOUNT-STATE-`. The prefix and date narrow a search before any
  grep does.
- When a claim rests on one note, **follow its links before answering**: the note it supersedes, and
  the notes that link back to it. A decision reversed elsewhere is the failure this step prevents.

## Grilling

The vault has no `docs/adr/` and no `CONTEXT.md`, so this is **`grill-me` territory, not
`grill-with-docs`** - grilling does not write decisions back to the repo.

Grill from evidence, never from memory:

1. **Pull first, ask second.** Run the route above and read what comes back before the first
   question. A question built on recalled context grills the wrong thing.
2. **One decision branch at a time**, and quote the note and its path when asserting what the vault
   says.
3. **Press hardest where the vault is thin.** An `ops-assumed.base` entry, a finding the tool bins
   as "assumed", an unowned item - those are where his answer actually adds information. Settled
   decisions with verbatim evidence do not need relitigating.
4. **Surface contradictions rather than resolving them.** `ops-contradictions.base` exists for this;
   two notes disagreeing is a finding to put in front of him, not a tie for you to break.
5. **Cite or abstain still binds under grilling.** "The vault does not cover this, so this one is
   yours" is a legitimate and useful grill question. Inventing a premise to grill against is not.

**6. Register-app accuracy** ("is the app on Vercel current / does it match the vault / are all
calls and sweeps reflected"):

```bash
node ~/dev/jove-hq/tools/register-app/audit.mjs
```

Mechanical, no judgment: per-dataset generation shas against the live source commits, the Vercel
production deployment against origin/master, every indexed call marked full-read, no full-read
note newer than the last sweep, and the app's action inbox drained. Exit 0 with every row FRESH/OK
is the only state in which "the app is up to date" may be asserted; any STALE row names its own
fix (regenerate, commit scoped, push — the push deploys). Never answer an is-it-current question
from memory of the last deploy; run the audit.

## Relaying the answer to Dhiraj

The tool speaks in F-### ids and evidence bins. Your answer does not:

- **Never cite F-### ids** - they are the filing system, not his interface. State the claim in plain
  language and name the real-world object (the call, the ticket, the file) instead.
- **Preserve the bins in substance**: a finding marked "assumed" (taken from a status column or
  summary) is reported as unverified, never in the same voice as one marked "observed".
- **Preserve status**: a RETRACTED finding is evidence about what was wrongly believed, never
  evidence for the claim.
- **Newest governs, older still binds its own layer**: a later decision supersedes an earlier one
  only on the point it actually addresses.
- **Answer first**, 1-4 tight sentences, then sources as repo-relative paths:

```
Answer: Certificates are out of the Labs MVP scope, deferred post-launch.

Sources:
- knowledge/jove-labs/current-state-reference.md
- knowledge/meetings/2026-07/2026-07-02-dhanur-jove-labs-handover.md
```

## Cite or abstain

If the ledger says it does not answer, and `--corpus` plus lexical search over the vault come back
empty: say **"not in the vault"** and name what it would take to find out (which surface, which
person). Never fabricate a decision, owner, date, or metric. A grounded "I don't know" beats a
confident guess.

## If the tool fails

```bash
node ~/dev/jove-hq/tools/sweep/az.mjs --check
```

Credentials live in `~/.zshrc` and are parsed from the profile, so an empty `env | grep AZURE` is
expected, not the problem. Exit 2 = could not run (creds); exit 1 = model error. A dead credential
is a finding to report, not an unknown to guess past. Fallback while blocked: route 3 (lexical)
still works for everything, including Labs.

## What NOT to do

- No Pinecone queries, no re-ingest, no repairing the stale mirror - frozen by decision, staleness
  is by design.
- Don't grep `knowledge/jove-labs/` as a *substitute* for ledger-ask on a Labs question: the ledger
  is the reconciled layer; raw notes contain superseded drafts that grep will happily surface as if
  current.
- Don't summarize the tool's output from memory - quote what it actually returned, translated per
  the relay rules.
- Don't answer from another vault or from model recall and present it as vault recall.
