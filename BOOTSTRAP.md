# BOOTSTRAP — Restoring this setup on a new Mac

This is the runbook to get from a fresh Mac + Claude subscription to the same orchestration setup as the source machine. Estimated time: **15–20 minutes**.

> **🚀 Fast path (recommended):** Run `Tooling/restore.sh`. It does steps 1–7 below in a single pass after one confirmation prompt. See [Tooling/README.md](Tooling/README.md). Step 7 (MCP secrets) is the only manual remainder. The steps below remain as a reference if you need to do anything partially or manually.

---

## 0. Prerequisites on the new Mac

- Claude Code installed (`brew install claude-code` or the official installer)
- Logged into your Claude subscription via `claude login`
- `git` and `curl` available (macOS ships both)
- This kit folder accessible (placed anywhere you like) — restore from iCloud / external drive / git remote
- Homebrew is **not** required up-front — `Tooling/restore.sh` installs it if missing

### Set `KIT_DIR` once (makes every command below location-independent)

The manual steps reference the kit through a `$KIT_DIR` variable, so they work no matter where you put this folder. From wherever you placed it:

```bash
cd "/path/to/Claude Agents and Skills (PORTABILITY KIT)"   # adjust to where you put it
export KIT_DIR="$PWD"
```

Keep this terminal open for the rest of the runbook. If you open a new shell, re-run those two lines. (The fast path — `Tooling/restore.sh` — self-locates and needs no `KIT_DIR`.)

---

## 1. Restore the global config

```bash
# Copy your global instructions back into ~/.claude/
cp "$KIT_DIR/CLAUDE-global.md" ~/.claude/CLAUDE.md
cp "$KIT_DIR/settings.json" ~/.claude/settings.json
```

The `settings.json` includes:
- Pre-allowed permissions (`Bash(*)`, `Edit(*)`, `Write(*)`, etc.)
- Experimental flag `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- The list of enabled plugins (these will install in step 4)
- The list of known marketplaces (these will register in step 4)

---

## 2. Restore the custom agents

```bash
mkdir -p ~/.claude/agents
cp "$KIT_DIR/Agents/"*.md ~/.claude/agents/
```

Verify:

```bash
ls ~/.claude/agents/ | wc -l   # should print 35
```

Claude Code auto-discovers agents on next session start. No restart command needed.

---

## 3. Restore the custom skills

```bash
mkdir -p ~/.claude/skills
# Copy each skill directory back
rsync -a "$KIT_DIR/Skills/" ~/.claude/skills/
```

Verify:

```bash
ls ~/.claude/skills/ | wc -l   # should print 106
```

> **Note:** On the source Mac, ~30 of these were *symlinks* to `~/.agents/skills/` (an external Mattpocock library). In this folder, those symlinks have already been **resolved** into real content — you do NOT need to install or restore `~/.agents/skills/` separately. Everything is self-contained.

> **Optional cleanup:** If you later want to switch back to the symlink-based layout (so updates to the upstream Mattpocock library propagate), see §7.

---

## 4. Re-install plugin marketplaces and plugins

Per `settings.json`, four marketplaces and eight plugins must be re-registered. **See [Plugins/README.md](Plugins/README.md) for the full inventory and per-plugin notes.**

### 4a. Marketplaces

```bash
# claude-plugins-official is registered by default — no action needed.

# Add superpowers marketplace
claude plugin marketplace add github obra/superpowers-marketplace

# Add karpathy skills marketplace
claude plugin marketplace add github forrestchang/andrej-karpathy-skills

# Vercel plugin marketplace was a LOCAL directory on the source Mac.
# See Plugins/README.md §5 for the recovery options on a new Mac.
```

### 4b. Plugins

```bash
claude plugin install figma@claude-plugins-official
claude plugin install vercel-plugin@vercel-vercel-plugin    # see Plugins/README.md §5
claude plugin install superpowers@superpowers-marketplace
claude plugin install superpowers-chrome@superpowers-marketplace
claude plugin install superpowers-developing-for-claude-code@superpowers-marketplace
claude plugin install superpowers-lab@superpowers-marketplace
claude plugin install andrej-karpathy-skills@karpathy-skills
claude plugin install github@claude-plugins-official
```

Verify:

```bash
claude plugin list   # expect 8 plugins, all enabled
```

The shipped `settings.json` (already copied in step 1) has the right `enabledPlugins` block, so no further toggling is needed.

---

## 5. Restore MCP servers (local + plugin-bundled)

**See [MCP/README.md](MCP/README.md) for the full MCP layered model.** Short version for restore:

### 5a. Local MCP servers (`~/.claude/mcp.json`)

```bash
# 1. Open the template, replace REDACTED_* with live tokens (n8n JWT lives in 1Password)
$EDITOR "$KIT_DIR/MCP/mcp.template.json"

# 2. Copy into place once secrets are filled in
cp "$KIT_DIR/MCP/mcp.template.json" ~/.claude/mcp.json
```

### 5b. Plugin-bundled MCP servers

Auto-restored when step 4 reinstalls the plugins. Nothing to do manually.

---

## 6. Restore account-bound Connectors

**See [Connectors/README.md](Connectors/README.md) for the full inventory and reattach procedure.** Short version:

1. **`claude login`** in the terminal → your Anthropic-account state (including all connectors) reattaches.
2. On first use, any OAuth-backed connector (Gmail, Drive, Calendar, Figma, Atlassian, Slack) will pop a browser prompt. Approve to rebind.
3. **Verify** — in a Claude Code session, ask: *"list all available MCP tool prefixes."* The output should match `Connectors/README.md` §4.

If any expected connector is missing, open *claude.ai → Settings → Connectors* and re-add it.

### Automation / loop heartbeat (account-bound — nothing to file-restore)

Like connectors, the **automation layer** reattaches automatically. After `claude login`, the scheduling stack (`/loop`, `/goal`, `/schedule`, `Cron*`, `mcp__scheduled-tasks__*`) is available immediately; `anthropic-skills:schedule` and the superpowers loop skills return when plugins reinstall (step 4). The operator's token-optimizer `hooks`/`statusLine` are **intentionally not vendored** (machine-specific path; the plugin re-establishes them). **See [Automations/README.md](Automations/README.md)** for the loop-engineering architecture, the heartbeat mechanisms, and the human-in-the-loop kit-maintenance loop.

---

## 7. Install supporting CLIs

If you used the fast path (`Tooling/restore.sh`), this is **already done** — `brew bundle` and `npm install -g` ran with the snapshot in `Tooling/Brewfile` + `Tooling/npm-globals.json`.

If doing it manually, the equivalent commands are:

```bash
# All host-side packages in one go
brew bundle --file="$KIT_DIR/Tooling/Brewfile"

# Global npm packages
cd "$KIT_DIR/Tooling"
node -e 'const list=require("./npm-globals.json").dependencies||{};
  Object.keys(list).filter(n=>n!=="npm").forEach(n=>console.log(n));' \
  | xargs -n1 npm install -g
```

See [Tooling/README.md](Tooling/README.md) for the inventory of what gets installed and why each package is there. If you use the `gws-forms` or Google Drive MCP, you'll also need Google OAuth set up on the new Mac — re-authenticate via the Claude Code MCP UI on first use.

---

## 8. (Optional) Re-establish the Mattpocock external library

If you want updates to the upstream Mattpocock skills to propagate automatically (instead of being frozen at this snapshot's version), restore the symlink layout:

```bash
# 1. Clone or restore the external library
mkdir -p ~/.agents
git clone <mattpocock-skills-source> ~/.agents/skills
# (Check the source URL — typically a private repo or local backup)

# 2. Identify which skills were symlinks on the source Mac.
#    The full list was: 3d-web-experience, code-review-excellence,
#    cra-to-next-migration, find-skills, flutter-* (20 skills),
#    framer-motion-animator, gws-forms, langfuse, postgresql-code-review,
#    product-management, r3f-best-practices, security-review, supabase,
#    supabase-postgres-best-practices, tanstack-start-best-practices,
#    threejs-animation, typescript-react-reviewer

# 3. For each of those, replace the copied directory with a symlink:
cd ~/.claude/skills
for s in 3d-web-experience code-review-excellence cra-to-next-migration \
         find-skills framer-motion-animator gws-forms langfuse \
         postgresql-code-review product-management r3f-best-practices \
         security-review supabase supabase-postgres-best-practices \
         tanstack-start-best-practices threejs-animation \
         typescript-react-reviewer; do
  rm -rf "$s"
  ln -s "../../.agents/skills/$s" "$s"
done

# 4. Flutter skills:
for s in ~/.agents/skills/flutter-*; do
  name=$(basename "$s")
  rm -rf "$name"
  ln -s "../../.agents/skills/$name" "$name"
done
```

Skip this section if you'd rather use the frozen-at-snapshot versions (simpler, no upstream dependency).

---

## 9. Verify the restoration

In a fresh terminal, run (re-establish `KIT_DIR` first, since a new shell won't have it):

```bash
# If this is a new shell, point KIT_DIR at the kit again:
cd "/path/to/Claude Agents and Skills (PORTABILITY KIT)" && export KIT_DIR="$PWD"

# Check agents
ls ~/.claude/agents/*.md | wc -l   # expect 35

# Check skills
ls ~/.claude/skills/ | wc -l       # expect 106 (or fewer if some are now symlinks)

# Check plugins
claude plugin list                  # expect 8 enabled plugins

# Check global instructions
head -30 ~/.claude/CLAUDE.md        # should start with "# Claude Code Configuration"

# Check host-side tooling (snapshot match)
brew bundle check --file="$KIT_DIR/Tooling/Brewfile"
                                    # expect "The Brewfile's dependencies are satisfied."

# Check global npm packages
npm list -g --depth=0               # should include @anthropic-ai/claude-code, @openai/codex, docx

# Launch Claude Code and ask:
#   "Confirm Engineering Manager mode is active and list available agents"
```

If Claude Code lists all 35 custom agents and acknowledges Engineering Manager mode in the response, restoration is complete.

---

## 10. Post-restore best practices

- Run `evaluating-skill-necessity` before adding any new skill (this is in CLAUDE-global.md anyway).
- Run `managing-skills-library` monthly to audit for drift.
- If you maintain context kernels in workspace repos (`<workspace>/.kernel/KERNEL.md`), pull those repos and the kernels come with them — no separate step.
- If you backed up per-workspace auto-memory (`~/.claude/projects/<workspace>/memory/`), see [MEMORY.md §3](MEMORY.md) for the restore procedure.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Specialist agent not discovered | Check `~/.claude/agents/<name>.md` has the right YAML frontmatter (`name:` matches what you dispatch with). |
| Skill not auto-triggering | Check `SKILL.md` frontmatter `description:` — the trigger phrases live there. |
| Plugin not appearing in skill list | `claude plugin list` to verify enabled; re-install if missing. |
| MCP server "not authenticated" | Run the auth flow per server (e.g., `nlm login` for NotebookLM). For HTTP MCPs in `mcp.json`, verify the JWT is current. |
| Settings.json permissions seem too permissive | They are intentional — the orchestrator never directly executes them, and dispatched specialists need them. If you want stricter scoping, edit `settings.json` to use granular `Bash(<cmd>)` patterns instead of `Bash(*)`. |
| Engineering Manager mode "I won't write code" appears in a dispatched subagent | This is a bug — the rule only binds the orchestrator. Re-read `CLAUDE-global.md` § Specialist Behavior; the override clause is there. If a specialist self-refuses, point it at that clause. |

---

## Capability dependency matrix

For each capability category, what *else* needs to exist on the new Mac for it to actually work. Skip any row where you don't use the capability.

| Capability | Layer | Host-side dependency | Where the secret lives |
|---|---|---|---|
| Vercel deploys & API | Plugin + Connector | `vercel` CLI (`npm i -g vercel`) | OAuth via `vercel login` |
| Vercel marketplace install | Plugin source | `vercel-marketplace-source/` in this kit (see Plugins/README.md §5) | — |
| Figma plugin (`use_figma`) | Plugin + Connector | Figma desktop or web open | OAuth via plugin's `authenticate` |
| Supabase MCP | Connector | — | Supabase access token (re-auth via Claude UI) |
| Slack messaging | Plugin/Connector | — | Slack OAuth via Claude UI |
| Gmail / Calendar / Drive | Connector | — | Google OAuth on first use |
| NotebookLM | Connector | `nlm` CLI (`npm i -g nlm`) + `nlm login` | Google account in `nlm` |
| Reddit search **read** | Connector | — | None (read-only safety boundary) |
| Reddit **write** (currently OFF) | Connector | `REDDIT_USERNAME` / `REDDIT_PASSWORD` env vars | Don't set unless intentional |
| Pinecone | Connector | — | Pinecone API key (set in MCP config when prompted) |
| Langfuse skill | Skill | `npx` available | Langfuse public/secret keys in env or per-project `.env` |
| `n8n` MCP | Local MCP | — | JWT in `mcp.template.json` → paste into `~/.claude/mcp.json` |
| Chrome MCPs (3 of them) | Connector | Chrome browser installed | OAuth via Claude UI where needed |
| `dart-mcp-server` | Connector | Flutter/Dart SDK installed | — |
| Greenfield Spec-Driven Dev | Skill | `specify` CLI installed | — |
| Most skills that shell out | Skill | `gh`, `jq`, `ripgrep`, `node`, `python` via Homebrew | — |

**Authoritative package list:** `Tooling/Brewfile` + `Tooling/npm-globals.json`. The matrix above lists *why* each tool is needed; the snapshot files list *exactly* what gets installed. They are kept in sync — if you add a new package on the source Mac, re-run `brew bundle dump --force` and `npm list -g --depth=0 --json` in `Tooling/` to refresh.

Running `Tooling/restore.sh` installs both sets in one pass. That covers ~90% of the host-side dependency surface; the remaining 10% (Vercel CLI, `nlm`, `specify`, etc.) are pulled in by the Brewfile's `uv` entries or by skills on-demand.

---

## Source-of-truth precedence (during a restore)

If something disagrees, this is the order to trust:

1. `~/.claude/CLAUDE.md` (live, after copying `CLAUDE-global.md` into place) — top priority
2. `~/.claude/settings.json` — plugin + permission state
3. `CLAUDE.md` (this folder's root) — orchestration documentation
4. `Agents/README.md` and `Skills/README.md` — roster-level documentation

If you discover a contradiction during restoration, fix it in the live `~/.claude/` first, then update this folder so future restorations are correct.
