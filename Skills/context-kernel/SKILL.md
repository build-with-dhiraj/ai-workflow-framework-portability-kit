---
name: context-kernel
description: Maintain .kernel/KERNEL.md so forked chats resume project state. Triggers on session-start, "where did we leave off".
---

# Context Kernel Skill

You are now responsible for maintaining a project context kernel that survives chat forks. The kernel is a single Markdown file at `<workspace>/.kernel/KERNEL.md` where `<workspace>` is the current working directory (the project root). An append-only daily log at `<workspace>/.kernel/log/YYYY-MM-DD.md` is the safety net.

## Purpose

In a long-running multi-session project, the user may start a new Claude Code chat (a "fork") at any time. Without the kernel, every fork is blind — they have to re-explain context. With the kernel, the orchestrator reads it as the first action on session start, briefs the user in 4–6 lines, and continues from where the prior chat left off.

After substantive turns, the kernel is updated so it never goes stale. The user reviews kernel changes via a per-response **"Kernel Updates"** block and corrects them at the top of their next prompt.

## Path discovery

- Workspace root = the current working directory (`pwd`).
- Kernel file = `<workspace>/.kernel/KERNEL.md`.
- Log directory = `<workspace>/.kernel/log/`.
- Daily log file = `<workspace>/.kernel/log/<YYYY-MM-DD>.md` (use system date in local timezone).

If `.kernel/KERNEL.md` does not exist in the workspace, this skill does NOT apply — that workspace has not been bootstrapped with a kernel. Do not auto-create one without the user's request.

## Kernel schema

The kernel uses this fixed structure. Section headings are required; their order is required; their presence is validated on every read.

```
# Project Kernel — <project name>
Last-Updated: <ISO8601 timestamp>
Kernel-Version: 1

## North Star
<1 paragraph: what we're building, for whom, why narrow>

## Locked Decisions
- [YYYY-MM-DD] <decision> — rationale: <1 line>
- ...

## Open Questions
- <question> — blocking: <what work it blocks>
- ...

## Active Artifacts
- <type>: `<absolute path>` — current thesis (3–5 lines), last touched: <YYYY-MM-DD>
- ...

## Threats & Landmines
- <adjacent competitor, dead-end already explored, thing not to relitigate>
- ...

## Pending Hand-offs
- <what the next chat / fork should pick up first, with enough detail to act>
- ...

## Fork Checkpoint
<optional — present only when user has explicitly forked here>
- Created: <YYYY-MM-DD HH:MM>
- From-context: <what was just done in the chat that produced this checkpoint>
- Resume instructions: <explicit next 1–3 actions>

## Historical Context (compacted)
<consolidate-memory output; trimmed periodically by the Kernel Steward>

## Resume Protocol
If you are reading this at session start: brief the user with the North Star (1 line), the most recent Locked Decision, the top Open Question, the Pending Hand-off, and the Fork Checkpoint (if present). End with: "Continue from hand-off, or pivot?"
```

## Read mode (session-start brief)

When you enter a session and detect a kernel at `<workspace>/.kernel/KERNEL.md`:

1. Read the file.
2. **Integrity check**:
   - Required H2 sections present: North Star, Locked Decisions, Open Questions, Active Artifacts, Threats & Landmines, Pending Hand-offs, Historical Context, Resume Protocol
   - `Last-Updated` field present and parseable as ISO8601
   - If invalid: read the most recent `.kernel/log/*.md` entry, surface the anomaly to the user, propose reconstruction. Dispatch the `Kernel Steward` agent with `reason: integrity-recovery`.
3. If valid: produce a 4–6 line brief in this format:

```
**Project state** (read from `.kernel/KERNEL.md`, last updated <date>):
- North Star: <one line>
- Most recent locked decision: <one line>
- Top open question: <one line>
- Pending hand-off: <one line>
- Fork checkpoint (if present): <one line>

Continue from hand-off, or pivot?
```

Do this BEFORE responding to the user's opening prompt content.

## Write mode (post-turn updates)

When a turn meets any update trigger (see below), edit `<workspace>/.kernel/KERNEL.md` directly using minimum-diff edits:

### Update triggers (DO update for)
- A decision was **locked** (user explicit "let's go with X" or implied closure of a debate)
- An **open question** opened or closed
- An **artifact** was modified, created, or had its thesis change (file under `outputs/` or the project's concept doc)
- A **threat** was identified or invalidated
- A **hand-off** changed (next session should do something different than what's currently listed)
- The user signaled a fork: "I'm forking here", "remember this for the fork", "lock this in"

### Do NOT update for
- Pure Q&A or explanation without state change
- User acknowledgments ("ok", "thanks", "got it")
- Read-only tool calls (listing files, searching, fetching)
- Speculative brainstorming the user hasn't endorsed
- Trivial corrections to the prior response

### Editing discipline
- **Preserve schema**: never delete a required H2 section, even if empty.
- **Never delete Locked Decisions** — only mark them superseded with a follow-on entry: `- [YYYY-MM-DD] SUPERSEDES: <old decision> — new direction: <X>`.
- **Pointers, not duplication**: store the path to an artifact + a 3–5 line distilled thesis; do not copy the full content of the artifact into the kernel.
- **Bump `Last-Updated`** to current ISO8601 timestamp on every edit.
- **Append a log entry** to `<workspace>/.kernel/log/<today>.md` (create the file if it doesn't exist) summarizing the diff in 1–3 lines.

### Cap target
- Keep `KERNEL.md` under 25KB.
- If editing pushes it past 20KB, **escalate to the Kernel Steward agent** with `reason: compaction` — do not attempt to compact inline.

## Per-response notification block

When a turn touched the kernel, the orchestrator MUST end its response with this block:

```
---
**Kernel updates** (provisional — confirm or correct in your next prompt):
- Added/Updated/Removed <section>: <one-line summary>
- ...
```

If a turn did not touch the kernel, omit the block entirely. **Silence is the signal.** Do not say "no kernel updates this turn" — that wastes the user's attention.

## Per-turn correction flow

At the start of every turn AFTER session start:
1. Check whether the user's prompt opens with a kernel correction signal (e.g., "looks good", "no, drop the X update", "actually change Y to Z").
2. If yes: apply the correction (edit or revert the relevant kernel entry, log the correction) BEFORE processing the rest of the prompt.
3. If the user said nothing about the prior kernel updates: treat them as implicitly confirmed and proceed.

## Escalation to Kernel Steward agent

Dispatch the `Kernel Steward` subagent (via the Agent tool) instead of editing inline when:

| Reason | When |
|---|---|
| `compaction` | Kernel > 20KB; Steward invokes consolidate-memory on the Historical Context section |
| `multi-section` | A single update touches 3+ H2 sections (e.g., a decision that invalidates an open question AND modifies an artifact thesis AND adds a threat) |
| `fork-checkpoint` | User signals "I'm forking here" — Steward writes the Fork Checkpoint section with explicit resume instructions |
| `integrity-recovery` | Read-mode integrity check failed; Steward reconstructs kernel from the most recent log entry |

For these cases, dispatch the Steward, return briefly, and emit the Kernel Updates block based on Steward's diff summary.

## Log entry format

Daily log at `<workspace>/.kernel/log/<YYYY-MM-DD>.md`. Append-only. Format per entry:

```
## <HH:MM> — <one-line summary>
- Section: <H2 name>
- Change: added | updated | removed | reverted
- Detail: <2–3 lines max>
```

Create the file with a `# Kernel Log — <date>` header on the first entry of the day.

## Coexistence

- **AGENTS.md** (if present at workspace root): independent Codex doctrine. Do not touch.
- **Global `~/.claude/CLAUDE.md`**: Engineering Manager mode rules apply. Kernel/skill/agent files are meta-config (allowed exception zone).
- **`anthropic-skills:consolidate-memory`**: invoked ONLY by the Kernel Steward agent, ONLY for the Historical Context section. Never invoked directly by the orchestrator.
- **`anthropic-skills:obsidian-vault`**: explicitly out of scope. The user does not want Obsidian dependency.

## Portability note (for skill maintainers)

This skill is workspace-agnostic. It discovers paths from CWD and never hard-codes a specific workspace. If a workspace has not been bootstrapped (no `.kernel/` directory), the skill does not apply — do not auto-bootstrap without explicit user request.

Workspace-specific instructions (project name, scope, north-star phrasing, custom rules) live in the workspace's `CLAUDE.md`, not in this skill.
