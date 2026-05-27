---
name: wrap-up
description: Archive the current Claude conversation into Pinecone (`jove-memory` index → `conversations` namespace) for permanent semantic recall. Use when substantial work has just been completed — files created/modified, decisions made, hypotheses moved, or user has acknowledged a milestone. Auto-PROPOSE when ≥2 trigger signals fire (never auto-execute silently). Can also be invoked manually via `/wrap-up [optional title]`.
---

# Wrap-up — session archiver

The "hard drive" half of the Karpathy + Pinecone architecture (see vault `[[Memory Architecture]]` and `[[CLAUDE]]` rule §5). Every substantial conversation gets a one-shot summary vectorized into Pinecone so future sessions can recall it semantically.

## When to trigger

**User invokes manually**: `/wrap-up [optional title]` → execute immediately.

**Auto-propose** (you ASK the user, never execute silently): when ≥2 of these signals fire in the current session:
- 3+ files created or significantly modified
- A new `decision`-type note appeared in `50 — Decisions & Bets/`
- User said "looks good", "approved", "ship it", "done", "let's continue", or similar milestone acknowledgment
- An architecture / CLAUDE.md change was made
- ≥30 minutes of active work since the last wrap-up
- User explicitly asked for a summary, status, or TLDR

**Propose like this** (don't be verbose):
> Looks like we just wrapped a substantial chunk — `{1-line description}`. Want me to `/wrap-up` so it's archived to Pinecone? (Or keep going — your call.)

If the user says yes → execute. If no → continue, don't re-ask for ~15 minutes.

## What it does (execution steps)

1. **Generate a structured summary** in this exact shape (markdown):
   ```markdown
   # {Title} — {YYYY-MM-DD}

   ## What changed
   - Files: {bulleted list of paths created or modified, with vault-relative paths}

   ## Decisions made
   - {Decision} → {Rationale}

   ## Hypotheses moved
   - 🟢 confirmed: {hypothesis} — {evidence}
   - 🔴 disconfirmed: {hypothesis} — {evidence}
   - 🟡 ambiguous: {hypothesis} — {gap}

   ## Open follow-ups
   - {Items carried forward}

   ## Key user quotes (intent signal)
   > "{verbatim quote}"
   ```
   Keep total summary **200-500 words**. This is a recall handle, not a transcript.

2. **Construct the Pinecone record**:
   - `id`: `convo-{YYYY-MM-DD}-{kebab-case-title}` (e.g. `convo-2026-05-23-pinecone-architecture-setup`)
   - `text`: the full markdown summary above (this is what gets embedded — the `fieldMap.text` field of the `jove-memory` index)
   - `date`: ISO `YYYY-MM-DD`
   - `project`: short tag (default `jove-labs`; override if session was about a different domain)
   - `files_touched`: array of vault-relative paths
   - `decision_count`: integer
   - `tags`: array of relevant tags (e.g. `["architecture", "pinecone", "wrap-up"]`)

3. **Upsert via Pinecone MCP**:
   ```
   mcp__pinecone__upsert-records:
     name: jove-memory
     namespace: conversations
     records:
       - id: {id}
         text: {summary}
         date: {date}
         project: {project}
         files_touched: {array}
         decision_count: {N}
         tags: {array}
   ```

4. **Append one line to `99 — Meta/log.md`** (per CLAUDE.md rule §1):
   ```
   ## [YYYY-MM-DD] query | wrap-up: {title} — archived to Pinecone (conversations namespace) — {N} files touched
   ```

5. **Confirm to user in one line**:
   > Archived as `{id}`. Recall later by asking "do you remember when we…" or "what did we decide about…".

## Companion behavior — recall before generating

When the user says **"do you remember when we discussed…"** / **"what did we decide about…"** / **"have we talked about…"** — *before* answering from session memory:

1. Search the `conversations` namespace:
   ```
   mcp__pinecone__search-records:
     name: jove-memory
     namespace: conversations
     query:
       inputs: { text: {user's question} }
       topK: 5
   ```
2. If a record scores ≥0.75 similarity, **cite the record id** in your answer: "Per `{id}` on {date}, we decided…"
3. If no record scores well, say so explicitly: "I don't see a wrap-up matching that. Either it wasn't archived, or it was before we set up Pinecone."

## Pre-Pinecone-index fallback

If `mcp__pinecone__list-indexes` doesn't show `jove-memory` (e.g. running before the index is created):
1. Write the summary to `99 — Meta/Wrap-ups/{id}.md` with frontmatter:
   ```yaml
   ---
   type: wrap-up
   status: pending_pinecone
   date: {YYYY-MM-DD}
   project: {project}
   files_touched: {array}
   ---
   ```
2. Once `jove-memory` exists, batch-upload all `pending_pinecone: true` files in one pass and flip the frontmatter to `status: archived`.

## What NOT to wrap up

- Single-question Q&A with no artifacts produced
- "What's the state of X?" status pings
- Skill discussions that didn't change vault state
- Conversations under ~10 minutes that produced nothing concrete
- Routine vault edits (rename a note, fix a typo)

## Anti-patterns

- ❌ Don't auto-execute. Always propose first.
- ❌ Don't store the full transcript — only the structured summary. Pinecone is semantic recall, not blob storage.
- ❌ Don't propose more than once per ~15-minute window if user declined.
- ❌ Don't include personally identifying info beyond what the user has already put in vault notes.
- ❌ Don't generate a wrap-up that's just "we talked about X" — it needs the decisions / file / hypothesis structure to be useful.
