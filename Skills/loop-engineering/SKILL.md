---
name: loop-engineering
description: Design and operate loop-engineered agent systems in Claude Code and Cursor. Use for loop engineering, harness design, Ralph loops, /loop, /goal, agent hub, self-improving agents, SKILL.md optimization, or choosing installable loop tooling from the research corpus.
---

# Loop Engineering

Operational skill distilled from **125-source full ingest** (93 non-GitHub line-indexed + 33 GitHub code audits). Load REFERENCE.md for doctrine; INSTALL.md for code-backed installs; CORPUS_INDEX.md for source digests.

## v2 requirement — evidence before recommendation

Before recommending any repo or install path:

1. Run `python3 scripts/load-digest.py --repo {slug}` OR read `data/repo-audits/{owner__repo}.md`
2. Cite evidence IDs (E###) or audit locators (`file:line`) in your answer
3. Flag README-vs-code mismatches when audit notes them

Do not recommend installs from REFERENCE.md alone.

## When to use

- User asks to design a loop, harness, or agent workflow
- Choosing between `/loop`, `/goal`, Routines, Ralph, or custom bash engines
- Picking an installable repo vs custom skill/agent
- Wiring verification, state write-back, or human-in-the-loop gates

## Decision tree

```
Need recurring agent work?
├─ Yes → Stop condition verifiable?
│   ├─ Yes → Maturity path (below)
│   └─ No → Fix stop condition first; do not schedule
└─ No → Single-shot skill dispatch; not a loop

Maturity path (jpoindexter / corpus consensus):
1. Reliable manual run (one skill, one outcome)
2. Encode as SKILL.md
3. Add state file or kernel write-back
4. Wrap in gated loop (mechanical + human gate)
5. Schedule via /loop or /goal
```

## Loop contract template

Every loop design MUST specify:

| Field | Question |
|-------|----------|
| **Trigger** | Schedule, event, or human `/loop` |
| **Input state** | What the agent reads (files, DB, kernel) |
| **Skill/playbook** | Which SKILL.md stages run |
| **Verifier** | Separate checker sub-agent or mechanical gate |
| **Stop condition** | Boolean test — not vibes |
| **Write-back** | What persists after each cycle |
| **Human gate** | When human must approve before next cycle |

## Harness primitives (use first)

| Primitive | Use when |
|-----------|----------|
| `/loop` | Fixed interval re-run of prompt or slash-command |
| `/goal` | Run until separate model grades "done" |
| Routines | Anthropic-documented recurring workflows |
| Sub-agents | Maker builds; checker verifies (never same agent) |
| Context kernel | Cross-session state at `.kernel/KERNEL.md` |

See portability kit `Automations/README.md` for heartbeat layer.

## Repo recommendation (code-backed)

**Required:** load audit before recommending.

```bash
python3 ~/.claude/skills/loop-engineering/scripts/load-digest.py --repo cobusgreyling/loop-engineering
python3 ~/.claude/skills/loop-engineering/scripts/load-digest.py --source S02
python3 ~/.claude/skills/loop-engineering/scripts/repo-pick.py --task "loop init"
```

Default layered stack (v2 code audit confirmed):
1. Harness `/loop` + `/goal` (built-in)
2. `cobusgreyling/loop-engineering` — 201 files read, score 9.62
3. Optional harness: `earendil-works/pi` (843 files)
4. Optional registry: `xpriment626/pi-factory` (68 files, SQLite blackboard)

## Dispatch rules

- **Loop architecture design** → dispatch `loop-engineering-architect` agent
- **Implementation** → dispatch domain specialist (never orchestrator)
- **Verification** → `superpowers:verification-before-completion` + code-reviewer
- **Skill authoring from loop learnings** → `write-a-skill` after one reliable manual run

## Anti-patterns

- Unattended loops without stop conditions
- Self-grading (same agent verifies its own work)
- Re-prompting full context each cycle instead of skills + state
- Confusing emosamastudio/agent-hub (job scheduler) with Sewell Agent Hub (entity registry)

## Refresh

Re-run when corpus grows:

```bash
python3 research/loop-engineering-agent-hub-2026/scripts/ingest_corpus_full.py
python3 research/loop-engineering-agent-hub-2026/scripts/audit_github_repos.py
python3 research/loop-engineering-agent-hub-2026/scripts/build_evidence_v2.py
python3 research/loop-engineering-agent-hub-2026/scripts/synthesize_doctrine_v2.py
```

Copy updated synthesis → REFERENCE.md, INSTALL.md, CORPUS_INDEX.md.
