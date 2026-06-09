# Memory System — Design & Restoration

This document explains how Claude remembers things across conversations on this Mac, what survives a Mac-replacement event, and what gets rebuilt automatically.

---

## 1. Two distinct memory layers

There are **two different persistent memory systems** at play. They don't overlap and they don't need to be synced.

### 1a. Auto-Memory (per-project, file-based)

**Location:** `~/.claude/projects/<workspace-slug>/memory/`

Each workspace gets its own folder. Inside:

- `MEMORY.md` — an **index** listing all memory files (lines after 200 are truncated, so it's deliberately short)
- One `.md` file per memory, with frontmatter:
  ```yaml
  ---
  name: <memory name>
  description: <one-line — used to score relevance in future conversations>
  type: <user | feedback | project | reference>
  ---
  ```

**What gets saved** — four memory types:

| Type | What | Example |
|---|---|---|
| `user` | Who you are, your role, expertise, goals | "Senior PM, deep Go background, new to React" |
| `feedback` | Corrections AND validated approaches | "Don't mock the database — got burned last quarter" |
| `project` | Active goals, decisions, deadlines, motivations | "Auth rewrite is compliance-driven, not tech-debt" |
| `reference` | Pointers to external systems | "Pipeline bugs live in Linear project INGEST" |

**What does NOT get saved** — code patterns, architecture, git history, debugging fixes, or anything documented in CLAUDE.md. These are derivable from current state.

**Format for `feedback` and `project` entries** — lead with the rule/fact, then a `**Why:**` line, then a `**How to apply:**` line. The "why" is what lets future-Claude judge edge cases.

### 1b. Project Context Kernel (per-workspace, schema-strict)

**Location:** `<workspace>/.kernel/KERNEL.md` + append-only journal at `<workspace>/.kernel/log/<YYYY-MM-DD>.md`

Used for long-running, multi-session projects where forking sessions is common. Maintained by the **`Kernel Steward` agent** (dispatched when kernel > 20KB, multi-section edits, fork checkpoints, or integrity recovery). The `superpowers:context-kernel` skill orchestrates inline reads/writes.

Schema is strict — H2 sections are fixed. If sections go missing or `Last-Updated` is malformed, that's an integrity-recovery dispatch for the Steward to handle from the journal.

---

## 2. What survives Mac replacement

| Layer | Survives? | How |
|---|---|---|
| Auto-Memory files | ❌ Local-only | Lost unless you back up `~/.claude/projects/<workspace>/memory/` for each workspace. Most are quickly rebuilt as the new Claude works in those projects. |
| Project Context Kernels | ✅ If repo is committed | `.kernel/` lives in the workspace — if the repo is on GitHub/GitLab, it survives. Otherwise back up the workspace directory. |
| Global CLAUDE.md | ✅ Mirrored here | `CLAUDE-global.md` in this folder. Copy back to `~/.claude/CLAUDE.md` on the new Mac. |
| Custom agents | ✅ Mirrored here | `Agents/*.md`. Copy back to `~/.claude/agents/` on the new Mac. |
| Custom skills | ✅ Mirrored here | `Skills/*/`. Copy back to `~/.claude/skills/` on the new Mac. |
| Plugin marketplace settings | ✅ Mirrored here | `settings.json`. Plugins themselves are re-fetched via the marketplace; see BOOTSTRAP.md. |
| MCP server registry | ⚠️ Template here | `mcp.template.json` has redacted secrets. Re-add tokens after restore. |

---

## 3. Restoring memory on the new Mac

After running [BOOTSTRAP.md](BOOTSTRAP.md), most of the system is back. For memory specifically:

### 3a. If you want to preserve auto-memory from specific workspaces

Before wiping the old Mac, archive each workspace's memory directory. These snippets use `$KIT_DIR` for the kit location — set it once with `cd "/path/to/Claude Agents and Skills (PORTABILITY KIT)" && export KIT_DIR="$PWD"` (per BOOTSTRAP.md §0):

```bash
# On the OLD Mac, before retirement:
for d in ~/.claude/projects/*/memory; do
  workspace=$(basename "$(dirname "$d")")
  if [ -f "$d/MEMORY.md" ]; then
    mkdir -p "$KIT_DIR/AutoMemory-Backup/$workspace"
    cp -R "$d"/* "$KIT_DIR/AutoMemory-Backup/$workspace/"
  fi
done
```

On the NEW Mac, after BOOTSTRAP.md and after Claude Code has created `~/.claude/projects/<workspace>/` for each workspace (this happens automatically when you `cd` into them and start a session), restore:

```bash
# On the NEW Mac:
for backup in "$KIT_DIR/AutoMemory-Backup/"*/; do
  workspace=$(basename "$backup")
  mkdir -p "$HOME/.claude/projects/$workspace/memory"
  cp -R "$backup"* "$HOME/.claude/projects/$workspace/memory/"
done
```

### 3b. If you don't bother to back up auto-memory

Don't worry — most of it is rebuilt within the first few conversations in each workspace. The system prompt's "auto memory" section instructs new-Claude to capture user/feedback/project/reference facts as they arise. Within 5–10 substantive turns per project, the most load-bearing memories return.

### 3c. Project Context Kernels

Already preserved if your project repos are pushed to a remote. If a kernel matters and the repo is local-only, **commit it before retiring the Mac** or back up the workspace directory.

---

## 4. The memory write/read protocol (for reference)

This is what the orchestrator does — kept here so you understand what's happening even when memory isn't explicitly invoked.

### When to write a memory

- User reveals their role, preferences, or knowledge → `user` memory
- User corrects an approach OR validates a non-obvious one → `feedback` memory
- You learn who, why, by-when → `project` memory
- User references an external system → `reference` memory
- All dates: convert relative ("Thursday") to absolute ("2026-05-15") before saving

### When to read a memory

- When memories seem relevant
- When the user references prior-conversation work
- MUST read when user says "remember," "recall," "check what I said about X"
- DO NOT use memory when user says to "ignore" or "not use" memory

### Stale memory protocol

Memory records can become wrong over time. **Before recommending anything from memory**:

1. If the memory names a file path → check the file exists
2. If the memory names a function or flag → grep for it
3. If the user is about to act on the recommendation → verify first

"The memory says X exists" is **not** the same as "X exists now."

---

## 5. Other persistence mechanisms (not memory)

These are different from memory and should not be confused with it:

| Mechanism | Scope | When to use |
|---|---|---|
| Plans (`Plan` agent / `superpowers:writing-plans`) | Current conversation | Aligning on approach before implementation |
| Todos (`TodoWrite` tool) | Current conversation | Breaking work into discrete trackable steps |
| Memory (this doc) | Across conversations | Anything you want future-Claude to know |
| Context Kernel | Across forked sessions | Long-running multi-session projects |
| Connector OAuth state | Across Macs (Anthropic-side) | Per-account, never in local memory; see [Connectors/README.md](Connectors/README.md) |

Rule of thumb: **if a piece of information is only useful within the current conversation, use a plan or todo — not memory.** And: **never write OAuth tokens or API secrets to memory** — they belong in `~/.claude/mcp.json` (with the redacted template mirrored here at `MCP/mcp.template.json`) or in account-bound connectors.

---

## 6. Memory in this specific folder

This kit folder has its own auto-memory directory under `~/.claude/projects/<slug-of-this-folder's-path>/memory/` (Claude Code derives the slug by replacing each `/` and space in the absolute path with `-`). As of the snapshot date (2026-05-27), it's empty — this conversation is the first substantive session in this workspace, so memory will populate as we continue working here.
