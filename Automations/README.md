# Automations — The Loop Heartbeat

This folder documents the **automation layer**: the scheduled, recurring triggers that turn a capable agent setup into an actual *loop* — a system that finds work, dispatches it, checks it, and remembers what's done, **without you prompting each step**.

It exists because of [Addy Osmani's "Loop Engineering"](https://addyosmani.com/blog/loop-engineering/): the leverage point is moving from *prompting agents* to *designing the loop that prompts them*. Of his five primitives + on-disk state, this kit was already strong on five — skills, sub-agents, plugins/connectors, worktrees, and memory — and thin on exactly one: **the heartbeat**. This folder closes that gap *as documentation*, because almost the entire automation stack is **harness- or account-bound** and reattaches at runtime rather than living in a file.

> **The headline:** like `Connectors/`, the automation layer mostly **survives a Mac swap automatically** — `/loop`, `/goal`, `/schedule`, scheduled-tasks and cron are Claude Code harness capabilities that reattach on `claude login`. There is almost nothing to *file-restore*. What this folder restores is the **design and the runbook** — so a future you (or future Claude) knows the loop architecture, why the heartbeat is intentionally not vendored, and how to run the kit's own maintenance loop while **staying the engineer**.

---

## 1. The kit against the six Loop-Engineering primitives

Audited 2026-06-16 against the live `~/.claude/` setup and this snapshot. (See the conversation that produced this folder for the full evidence-grounded findings.)

| # | Primitive | Loop job | This kit | Where it lives |
|---|---|---|---|---|
| 1 | **Automations** | discovery + triage on a schedule | 🔴 **thin** | this folder (harness-bound; documented, not vendored) |
| 2 | **Worktrees** | isolate parallel agents | 🟡 partial | `Agents/engineering-git-workflow-master.md` + `superpowers:using-git-worktrees` (plugin) |
| 3 | **Skills** | codify project knowledge | 🟢 strong | `Skills/` (115 vendored, self-contained) |
| 4 | **Plugins / connectors** | plug into real tools (MCP) | 🟢 strong | `MCP/`, `Plugins/`, `Connectors/` |
| 5 | **Sub-agents** | maker ≠ checker | 🟢 strong | `Agents/` (35; checkers: Code Reviewer, qa-expert, Security Engineer) |
| 6 | **State / memory** | on-disk done/next | 🟢 strong design | `MEMORY.md`, `Skills/context-kernel/` |

**Cross-cutting note:** the kit vendors the **WHAT** superbly but several loop-critical **HOWs** are plugin- or harness-provided — *named and recoverable, but not vendored*: worktree isolation (`superpowers:using-git-worktrees`), parallel dispatch (`superpowers:dispatching-parallel-agents`), the stop-condition verifier (`superpowers:verification-before-completion`), and the scheduler (harness `/loop` `/goal` `/schedule`). They restore via `claude plugin install` + `claude login`, not by copying files. Treat the superpowers plugin (pinned in `Plugins/installed_plugins.json`) as load-bearing for the loop.

---

## 2. The harness scheduling stack (account/harness-bound)

These are the heartbeat mechanisms. None is stored in a kit file; all are available at runtime after a normal Claude Code install + `claude login`.

| Mechanism | What it does | Restores via |
|---|---|---|
| `/loop` | re-run a prompt or slash-command on an interval (or self-paced) | harness (built-in) |
| `/goal` | run **until a verifiable condition holds**; a *separate* model grades "done" after each turn (maker ≠ checker baked into the stop condition) | harness (built-in) |
| `/schedule` | create/list/run scheduled remote agents (cron routines), incl. one-time runs | harness (built-in) |
| `mcp__scheduled-tasks__*` | programmatic create/list/update of scheduled tasks | harness MCP |
| `Cron*` tools (`CronCreate`/`CronList`/`CronDelete`) | cron primitives for autonomous loops | harness MCP |
| `anthropic-skills:schedule` | scheduling skill (bundled) | plugin reinstall |
| GitHub Actions (`schedule: cron:`) | off-machine recurring runs that survive closing the laptop | your project repo's `.github/workflows/` (NOT this kit) |

> The `github-actions` skill in `Skills/` teaches the `cron:` pattern, but as **user-project CI** material — it is not a heartbeat for this kit.

---

## 3. Hooks & statusLine (the per-event surface)

`settings.json` can carry a `hooks` block (shell commands fired on `SessionStart`/`PreToolUse`/`PreCompact`/etc.) and a `statusLine` — the *event-driven* cousin of the scheduled heartbeat.

**This kit deliberately does NOT vendor them.** The operator's live hooks/statusLine are token-optimizer-provided and hardcode a machine-specific path (`/Users/Dhiraj/.claude/skills/.archive-token-optimizer-pkg/…`). Copying them verbatim would bake a dead path into the snapshot. The token-optimizer plugin re-establishes them on a fresh Mac. (See the `Skills/README.md` 2026-06-11 changelog where this choice is logged.)

If you ever want a *portable* hook (e.g. a repo-relative pre-commit guard), add it to a `settings.template.json` with `$HOME`-relative paths — never absolute `/Users/<you>/` paths.

Plugin-bundled event hooks (`Plugins/vercel-marketplace-source/hooks/`, `Skills/claude-seo/hooks/`) ride along with their plugins and are not part of this layer.

---

## 4. n8n — the one vendored automation pointer

`MCP/mcp.template.json` carries a single local MCP server, `n8n` ("fires workflows from Claude"). The **schedule itself lives off-kit in n8n cloud**, and the JWT is redacted. So the *pointer* is captured but the *recurring job* is not.

To make a real scheduled job restorable, export the relevant n8n workflow JSON (sanitized) into this folder alongside a note — then the heartbeat is an artifact, not an opaque cloud cron behind a secret.

---

## 5. The kit's own loop — `/kit-maintenance` (human-in-the-loop)

The most authentic loop for *this* repo is the **live-vs-kit drift audit** — the exact thing done by hand to keep the snapshot honest (skills appearing in `~/.claude/skills/` but not vendored, Brewfile/npm drift, stale counts). Here it is as a runbook you can drive on a cadence. It is **deliberately human-gated**: the loop *surfaces* and *prepares*, you *approve* and *merge*.

```
HEARTBEAT   (you, via /loop or /schedule — weekly)
   │
   ▼
TRIAGE      Compare live ~/.claude/ vs this kit:
            • agents:   ls ~/.claude/agents vs Agents/
            • skills:   ls ~/.claude/skills vs Skills/   (the badge already self-counts)
            • brew/npm: brew bundle dump / npm ls -g  vs  Tooling/
            • settings/plugins/mcp: diff live vs snapshot
            → write findings to a PROGRESS file / triage inbox
   │
   ▼
DISPATCH    For each drift item worth capturing, the orchestrator dispatches a
            specialist (Technical Writer for docs, git-workflow-master for the
            commit) — in a git worktree if two run in parallel.
   │
   ▼
VERIFY      maker ≠ checker:  Code Reviewer + evaluating-agent-behavior +
            superpowers:verification-before-completion grade the change
            against "the snapshot now matches live, counts are right."
   │
   ▼
HUMAN GATE  You review the triage summary and approve. Nothing auto-merges.
   │
   ▼
COMMIT      git-workflow-master commits + pushes; counts/badge update.
```

Every noun above already exists in the kit. The only pieces that aren't vendored are the **scheduled trigger** (harness `/schedule`) and the **PROGRESS spine** (see §6) — by design.

---

## 6. State spine for the loop

A loop needs on-disk memory of what's done/next (Osmani's 6th piece). The kit's `MEMORY.md` + `Skills/context-kernel/` already define this:

- **Per-project loops:** reuse the context kernel's `## Pending Hand-offs` and `## Fork Checkpoint` sections (`Skills/context-kernel/SKILL.md`) — that *is* a done/next file.
- **The kit-maintenance loop:** a lightweight `PROGRESS.md` (uncommitted scratch, or a Linear board via MCP) listing open drift items. Keep it outside the single conversation — "the agent forgets, the repo doesn't."

---

## 7. Stay the engineer (the non-negotiable part)

Osmani's closing warning, mapped to this kit's verifiers — the reason a loop is a force multiplier *with* judgment and a liability *without*:

1. **Verification is on you.** An unattended loop is a loop making mistakes unattended. The kit's stop condition must run through `engineering-code-reviewer` + `evaluating-agent-behavior` + `superpowers:verification-before-completion` — never let the maker grade its own work. "Done" is a claim, not a proof.
2. **Comprehension debt.** Read what the loop produced. The faster it ships code you didn't write, the wider the gap between what exists and what you understand. The human gate in §5 exists for this.
3. **No cognitive surrender.** Designing the loop is the cure when done with judgment, the accelerant when done to avoid thinking. The loop doesn't know the difference. You do.

> **Build the loop. But build it like someone who intends to stay the engineer, not just the person who presses go.**

---

## 8. Restoration

Nothing in this layer needs file-restoration beyond this README. After a normal Claude Code install + `claude login`:

- `/loop`, `/goal`, `/schedule`, `Cron*`, `mcp__scheduled-tasks__*` are available immediately (harness).
- `anthropic-skills:schedule` and the superpowers loop skills return when plugins reinstall (`BOOTSTRAP.md` §4).
- Re-establish any token-optimizer hooks/statusLine via that plugin (not from this kit).
- Re-paste the `n8n` JWT (`MCP/README.md`) if you use that workflow trigger.
- Then drive the §5 maintenance loop on whatever cadence you like — **with the human gate intact.**
