---
name: building-claude-portability-kit
description: Snapshot Claude Code setup (agents, skills, plugins, MCP, tooling) into a portable folder. Use for backup or Mac migration.
---

# Building a Claude Portability Kit

## Philosophy — capability preservation, not work preservation

The goal is to preserve the **capability set** the user has built up — agents, skills, plugins, integrations, orchestration logic, host-side tooling — and **not** their work-in-progress (auto-memory, saved plans, per-project state). When the user pushes back on backing up project-level state, accept it: the kit gets smaller, cleaner, and the restore is faster.

Concrete success criterion: **drop the kit on any new Mac → `claude login` → run one script → working stack in ~20 minutes.**

If you find yourself capturing things that "might be useful" without a clear capability they preserve, stop and challenge it. The kit is not a backup utility.

---

## The seven-folder skeleton

Every portability kit gets exactly this shape. Folder boundaries are not arbitrary — they match the seven distinct restoration paths.

```
<KitName>/
├── CLAUDE.md            ← orchestration logic, precedence rules, org chart
├── MEMORY.md            ← memory-system design + restoration paths (descriptive)
├── BOOTSTRAP.md         ← step-by-step new-Mac runbook
├── CLAUDE-global.md     ← live snapshot of ~/.claude/CLAUDE.md
├── settings.json        ← live snapshot of ~/.claude/settings.json
├── Agents/              ← README + every custom agent .md
├── Skills/              ← README + every active skill dir (symlinks resolved!)
├── MCP/                 ← README + mcp.template.json with secrets REDACTED
├── Plugins/             ← README + installed_plugins.json + known_marketplaces.json + local-dir marketplace cache
├── Connectors/          ← README only (account-bound, no local files)
└── Tooling/             ← README + Brewfile + npm-globals.json + restore.sh
```

The **canonical worked example** is the "Claude Agents and Skills (PORTABILITY KIT)" folder this skill ships inside — when filling in a new kit, reference its structure and tone.

---

## Phase 1 — Recon the source machine

Inventory in parallel — this is read-only and fast:

```bash
ls -la ~/.claude/
ls -la ~/.claude/agents/
ls -la ~/.claude/skills/         # note which entries are lrwxr-xr-x (symlinks)
cat ~/.claude/plugins/installed_plugins.json
cat ~/.claude/plugins/known_marketplaces.json
cat ~/.claude/settings.json
cat ~/.claude/mcp.json                          # WARNING: contains secrets
cat ~/.claude/mcp-needs-auth-cache.json         # account-bound connector inventory
```

Look for:
- **Symlinked skills** → they target an upstream library (commonly `~/.agents/skills/`). Resolve them on copy.
- **Local-directory marketplace sources** in `known_marketplaces.json` → the actual marketplace lives in `~/.cache/plugins/<slug>/`. That cache directory must be embedded in the kit or the marketplace won't reinstall.
- **Secrets in mcp.json** → Bearer JWTs, API keys, OAuth tokens. Never copy verbatim.

Also check for things you might NOT need to capture (often misled-into-snapshotting):
- `~/.claude/commands/` — only if it exists (custom slash commands)
- `~/.claude/keybindings.json` — only if it exists
- `hooks` key in settings.json — only if user-defined (not plugin-provided)

---

## Phase 2 — Map the layered architecture

The kit's root `CLAUDE.md` documents how the pieces fit together. Use seven layers:

| # | Layer | Examples |
|---|---|---|
| 1 | **Orchestration** | Top-level Claude Code session, Engineering Manager mode |
| 2 | **Process skills** | brainstorming, tdd, diagnose, gepetto, grill-me, prototype |
| 3 | **Specialist agents** | engineering-frontend-developer, engineering-solidity-…, etc. |
| 4 | **Implementation skills** | supabase, threejs-animation, flutter-*, langfuse |
| 4½ | **Tools & integrations** (orthogonal) | MCP servers, plugin-bundled MCPs, account connectors |
| 5 | **Memory & state** | auto-memory, context kernel |
| 6 | **Governance** | evaluating-skill-necessity, managing-skills-library |

Layer 4½ is **orthogonal** to the agent stack — any layer can call any tool. Diagram this explicitly; it prevents the user from thinking integrations are owned by one specialist.

---

## Phase 3 — Resolve precedence between overlapping skills

The kit must answer "when two skills could do the job, which one wins?" Document explicit rules and concrete mappings. Typical contradictions in a mature setup:

| Job | ✅ Use | ❌ Don't use |
|---|---|---|
| TDD | `tdd` (Mattpocock) | `superpowers:test-driven-development` |
| Debugging | `diagnose` (Mattpocock) | `superpowers:systematic-debugging` |
| Writing a new skill | `write-a-skill` (Mattpocock) | `superpowers:writing-skills` |
| Architectural pre-planning | `gepetto` | `superpowers:writing-plans` (use AFTER gepetto) |
| Vercel deployment | `vercel-plugin:*` skills | local `vercel-deployment` (deprecated) |

Also document "narrowest-match-wins" cluster cascades — e.g., for 3D web work: `threejs-animation` (animation-specific) → `r3f-best-practices` (R3F non-animation) → `3d-web-experience` (general).

And: **user instructions always override any skill.**

---

## Phase 4 — Copy with symlink resolution

```bash
# Agents are plain .md files
cp ~/.claude/agents/*.md <Kit>/Agents/

# Skills MUST resolve symlinks (-L flag) so the kit is self-contained
rsync -aL --exclude='.archive' ~/.claude/skills/ <Kit>/Skills/

# Plugin manifests
cp ~/.claude/plugins/installed_plugins.json <Kit>/Plugins/
cp ~/.claude/plugins/known_marketplaces.json <Kit>/Plugins/

# Local-directory marketplace cache (CRITICAL — without it the marketplace fails to reinstall)
mkdir -p <Kit>/Plugins/<marketplace-slug>-source/
rsync -a ~/.cache/plugins/<marketplace-slug>/ <Kit>/Plugins/<marketplace-slug>-source/

# Settings + global CLAUDE.md
cp ~/.claude/settings.json <Kit>/
cp ~/.claude/CLAUDE.md <Kit>/CLAUDE-global.md
```

The `-L` flag on rsync is the make-or-break detail. Without it the kit holds dead symlinks; with it the kit is portable.

---

## Phase 5 — Redact secrets in templates

Never copy `mcp.json` verbatim. Create `MCP/mcp.template.json` with placeholders:

```json
{
  "_comment": "Replace REDACTED_* with live secrets on the new Mac.",
  "mcpServers": {
    "<server-name>": {
      "type": "http",
      "url": "https://...",
      "headers": { "Authorization": "Bearer REDACTED_PUT_<NAME>_TOKEN_HERE" }
    }
  }
}
```

Then BOOTSTRAP.md instructs the user to paste live secrets from their password manager.

---

## Phase 6 — Document the three MCP/integration layers

This is where users get confused. Explain explicitly:

| Layer | Where configured | Survives Mac wipe? |
|---|---|---|
| **Local MCP** | `~/.claude/mcp.json` (manual) | ⚠️ Only the file — secrets must be re-pasted |
| **Plugin-bundled MCP** | `~/.claude/plugins/cache/<plugin>/` | ✅ Auto-restored when plugin reinstalls |
| **Account Connectors** | claude.ai → Settings → Connectors | ✅ Auto-reattach on `claude login` |

Bulk of integrations are usually category 3 — derive the inventory from `~/.claude/mcp-needs-auth-cache.json`.

---

## Phase 7 — Capture host-side tooling

```bash
mkdir -p <Kit>/Tooling
brew bundle dump --force --file=<Kit>/Tooling/Brewfile
npm list -g --depth=0 --json > <Kit>/Tooling/npm-globals.json
```

`brew bundle dump` captures **leaf packages only** — that's correct. Transitive deps auto-pull on reinstall. Don't try to capture everything `brew list` returns; you'll over-specify.

If the user uses pyenv, rbenv, mise, asdf — capture those configs too. Otherwise skip.

---

## Phase 8 — Write the restore script

Critical patterns:

- `#!/usr/bin/env bash` + `set -euo pipefail`
- Single `[y/N]` confirmation at the top
- **Copy `settings.json` early** (around step 4 of 7). The shipped `settings.json` has `"Bash(*)"` in `permissions.allow`, so after that step Claude Code stops asking permission for each subsequent command in the run.
- Every operation must be idempotent: `rsync`, `brew bundle`, `npm install -g`, `claude plugin install` all skip already-installed
- Wrap `claude plugin marketplace add` in `|| true` (duplicates throw)
- Final step is **manual** — print instructions to paste the live secrets into `mcp.template.json`

Skeleton:

```bash
#!/usr/bin/env bash
set -euo pipefail
KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_HOME="$HOME/.claude"

read -r -p "Continue? [y/N] " confirm
[[ "$confirm" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }

# 1. Homebrew (install if missing)
# 2. brew bundle --file=$KIT_DIR/Tooling/Brewfile
# 3. global npm packages from npm-globals.json
# 4. cp settings.json and CLAUDE-global.md into ~/.claude/  ← Bash(*) becomes allowed here
# 5. rsync Agents/ and Skills/ into ~/.claude/, --exclude='README.md'
# 6. Restore Vercel-style local-dir marketplace cache, register marketplaces, install plugins
# 7. Print manual-step instructions for MCP secrets
```

---

## Phase 9 — Document and cross-reference

Each folder gets its own README. The root `CLAUDE.md` has an inventory table with one row per folder, and a source-of-truth precedence:

1. Live `~/.claude/CLAUDE.md` — highest (after restore)
2. The folder's own README — closer to its source
3. Root `CLAUDE.md` — general orchestration

When these disagree, the higher tier wins. State this explicitly in the kit.

The BOOTSTRAP.md must have:
- A "fast path" callout at the very top pointing at `Tooling/restore.sh`
- Numbered steps 0–10 for the manual path (in case someone wants to do it piecemeal)
- A **capability dependency matrix** (which capability needs which CLI / env var / OAuth flow)
- A troubleshooting section
- Source-of-truth precedence rules

---

## Phase 10 — Verify

After running the restore on a new Mac:

```bash
# Count parity
ls ~/.claude/agents/*.md | wc -l    # match Agents/ count
ls ~/.claude/skills/ | wc -l        # match Skills/ count
claude plugin list                   # match installed_plugins.json

# Tooling parity
brew bundle check --file=<Kit>/Tooling/Brewfile   # "satisfied"
npm list -g --depth=0                              # match npm-globals.json

# Smoke test
# Launch claude, ask: "Confirm Engineering Manager mode is active and list all custom agents"
```

---

## What NOT to capture

This is as important as what to capture. Refuse to add these even if asked:

| Don't capture | Why |
|---|---|
| OAuth tokens, JWTs, API keys | Security failure. Always redact and document where the live secret lives (1Password) |
| `~/.claude.json` | Contains account-bound state; auto-restored on `claude login` |
| `~/.claude/projects/<workspace>/memory/` | Per-workspace work; not a capability |
| `~/.claude/plans/`, `~/.claude/todos/`, `~/.claude/sessions/` | Ephemeral conversation state |
| `~/.claude/telemetry/`, `~/.claude/cache/`, `~/.claude/shell-snapshots/` | Local-only state, no value to preserve |
| System packages (`git`, `python3`, `curl`) | Come from macOS; don't pin |
| Per-project `.claude/`, `.kernel/`, `.specify/` directories | Live in the project repo; survive via git remote, not via this kit |
| Shell config (`~/.zshrc`, `~/.bash_profile`) | Out of scope — not a capability, and the user usually has strong opinions |

---

## Common pitfalls

1. **Forgetting `rsync -L` for skills** → kit holds dead symlinks → kit isn't portable.
2. **Including OAuth tokens in `mcp.template.json`** → security failure. Always redact.
3. **Inventing brew/npm package lists** instead of dumping live state → snapshot drifts from reality immediately.
4. **Skipping the local-directory marketplace cache** → the Vercel-style local-dir marketplaces fail to reinstall, blocking entire plugins.
5. **Asking for per-command permission in `restore.sh`** → wrong. Copy `settings.json` early so `Bash(*)` is allowed for the remainder of the script.
6. **Capturing work-in-progress without asking** → over-scoping. When in doubt, ask the user what they care about: capability or work?
7. **Writing skill precedence rules without concrete examples** → vague. Always show the "use X not Y" mappings.
8. **One giant README at root, no per-folder READMEs** → users can't drill in. Each folder gets its own README.
9. **Forgetting to update top-level docs after adding a new folder** → stale cross-references. After any structural change, re-audit `CLAUDE.md` §1 (inventory) and §8 (source-of-truth) plus `BOOTSTRAP.md` step list.

---

## Maintenance — keeping the kit current

When the source machine changes (new agent, new plugin, new brew package), re-snapshot:

```bash
# Custom agents
cp ~/.claude/agents/*.md <Kit>/Agents/

# Skills (resolve symlinks!)
rsync -aL --exclude='.archive' --delete ~/.claude/skills/ <Kit>/Skills/

# Plugin manifests
cp ~/.claude/plugins/{installed_plugins,known_marketplaces}.json <Kit>/Plugins/

# Global config
cp ~/.claude/CLAUDE.md <Kit>/CLAUDE-global.md
cp ~/.claude/settings.json <Kit>/

# Host-side tooling
brew bundle dump --force --file=<Kit>/Tooling/Brewfile
npm list -g --depth=0 --json > <Kit>/Tooling/npm-globals.json
```

Run this monthly, or any time the user mentions adding/removing a capability.

---

## Workflow at a glance

```
Recon ──► Map layers ──► Resolve precedence ──► Copy (resolve symlinks)
                                                       │
                                                       ▼
                       Redact secrets ◄──── Document MCP/Connector layers
                              │
                              ▼
                      Capture tooling ──► Write restore.sh ──► Cross-link READMEs
                                                                        │
                                                                        ▼
                                                                     Verify
```

The output of a successful run is a folder a future-you (or future-Claude) can pick up cold and turn back into a working machine.
