# Plugins — Roster & Restoration

Plugins are bundled packages that ship a curated mix of skills, agents, and MCP servers. They're managed via the Claude Code `plugin` CLI and registered marketplaces. This folder snapshots **which plugins were installed**, **which marketplaces they came from**, and how to restore them on a new Mac.

> **Where the live state lives on the Mac:** `~/.claude/plugins/installed_plugins.json` + `~/.claude/plugins/known_marketplaces.json` + `~/.claude/settings.json` (`enabledPlugins` section).
> **Restoration:** the snapshot files in this folder + the install commands below.

---

## 0. Delivery tiers — the thing to understand first

There are **two** kinds of plugin, and only one has files. Getting this wrong is
what makes the roster look broken.

| Tier | Where the files are | Count | In `installed_plugins.json`? | Captured here? |
|---|---|---|---|---|
| **1 — CLI plugins** | `~/.claude/plugins/cache/` | **13** | ✅ yes | ✅ **yes** |
| **2 — App-delivered** | **nowhere on disk** | ~10 | ❌ no | ❌ no — nothing to copy |

Tier 2 verified 2026-08-13: a filesystem-wide search for `desktop-commander`,
`searchfit-seo`, `bigdata-com`, `miro`, `auth0`, `zapier`, `anthropic-skills`,
`slack-by-salesforce`, and `product-tracking-skills` returned **NOT FOUND**.
The desktop app provisions them at runtime into a session-scoped cache.
`ListPlugins` returns empty; `ListSkills` returns only the 6 claude.ai account
skills. They reattach on `claude login` — there is no restore step, and adding
one is not possible.

**If a tier-2 plugin is missing after a restore, you are not logged in.** Do not
try to add it to this folder.

### Two local-directory marketplaces need their source restored FIRST

`restore.sh` step 6 rsyncs both before registering anything:

| Marketplace | Source in this folder | Provides |
|---|---|---|
| `vercel-vercel-plugin` | `vercel-marketplace-source/` | `vercel-plugin` (installed, disabled) |
| `agricidaniel-seo` | `claude-seo-source/` | `claude-seo` — 25 skills + 18 agents |

`claude-seo` was, until 2026-08-13, loose in `~/.claude/skills/` with no
registration anywhere, loading only because Claude Code auto-discovers a
`.claude-plugin/marketplace.json` there and synthesises a `skills-dir`
marketplace. It is now registered properly, so it survives a rebuild.

### `marketplace add` syntax — a real trap

```bash
claude plugin marketplace add obra/superpowers-marketplace          # ✅ correct
claude plugin marketplace add github obra/superpowers-marketplace   # ❌ fails
```

The `github` / `git` / `directory` keyword forms are **not valid** in CLI
2.1.223 — they fail with `Invalid marketplace source format`. Every marketplace
line in `restore.sh` used the keyword form and was wrapped in `|| true`, so the
adds failed silently and every plugin install after them failed too. Fixed
2026-08-13.

---

## 1. The two kinds of plugin you have

### 1a. Local Claude Code plugins (13) — fully captured here

These show up in `installed_plugins.json` and are managed by the `claude plugin` CLI. They are the authoritative scope of "what Claude Code on this Mac has installed."

### 1b. Account / Cowork plugins — captured by reference

These show up in `~/.claude/mcp-needs-auth-cache.json` with `plugin:<plugin-name>:<connector-name>` keys but **don't** appear in `installed_plugins.json`. They were installed via Claude Desktop / Cowork, which is account-bound — they reattach on `claude login`. See [../Connectors/README.md](../Connectors/README.md) for the inventory.

---

## 2. Local plugins — what's installed (13)

Versions verified against live `installed_plugins.json` on 2026-08-13.

| Plugin | Marketplace | Version | Scope | What it ships |
|---|---|---|---|---|
| `figma` | `claude-plugins-official` | 2.2.68 | project + user | Figma MCP server (`use_figma`) + 12 Figma skills |
| `vercel-plugin` | `vercel-vercel-plugin` | 0.24.0 | project | Vercel CLI/API wrapper + 29 Vercel skills + Vercel MCP — **installed but disabled** |
| `superpowers` | `superpowers-marketplace` | 6.1.0 | project + user | 14 process skills: brainstorming, writing-plans, executing-plans, subagent-driven-development, dispatching-parallel-agents, verification-before-completion, using-git-worktrees, finishing-a-development-branch, requesting/receiving-code-review, systematic-debugging, test-driven-development, writing-skills, using-superpowers |
| `superpowers-chrome` | `superpowers-marketplace` | 3.0.4 | user | `browsing` skill + `browser-user` agent + Chrome DevTools Protocol MCP |
| `superpowers-developing-for-claude-code` | `superpowers-marketplace` | 0.3.1 | user | `working-with-claude-code`, `developing-claude-code-plugins` |
| `superpowers-lab` | `superpowers-marketplace` | 0.5.0 | user | `windows-vm`, `mcp-cli`, `finding-duplicate-functions`, `using-tmux-for-interactive-commands` |
| `andrej-karpathy-skills` | `karpathy-skills` | 1.0.0 | user | `karpathy-guidelines` (behavioral coding guardrails) |
| `github` | `claude-plugins-official` | unknown | user | GitHub-related slash commands and helpers — ships no skills |
| `ponytail` | `ponytail` | 4.8.4 | user | 6 skills — the lazy-senior-dev response discipline + `/ponytail` levels |
| `youdotcom-agent-skills` | `claude-plugins-official` | 0.4.0 | user | 5 `you:*` search/research skills |
| `claude-seo` | `agricidaniel-seo` | 1.9.9 | user | **25 skills + 18 agents** — full SEO suite. Local-directory marketplace, source in `claude-seo-source/` |
| `productivity` | `knowledge-work-plugins` | 1.3.1 | user | 4 skills + MCP connectors for Asana, ClickUp, Linear, Monday, Notion, Slack, Atlassian |
| `cowork-plugin-management` | `knowledge-work-plugins` | 0.2.2 | user | 2 skills for authoring/customising Cowork plugins |

**Two skill-precedence notes (also in [../CLAUDE.md §4](../CLAUDE.md)):**

- `superpowers:systematic-debugging` is shadowed by local `diagnose` (Mattpocock). Use `diagnose`.
- `superpowers:test-driven-development` is shadowed by local `tdd` (Mattpocock). Use `tdd`.
- `superpowers:writing-skills` is shadowed by local `write-a-skill` (Mattpocock). Use `write-a-skill`.

---

## 3. Marketplaces (7) — where the plugins come from

Snapshot in `known_marketplaces.json` next to this README.

| Marketplace | Source type | Source | Notes |
|---|---|---|---|
| `claude-plugins-official` | GitHub | `anthropics/claude-plugins-official` | Default — registered by Claude Code at install time. No action needed. |
| `superpowers-marketplace` | GitHub | `obra/superpowers-marketplace` | Public repo, `autoUpdate: true`. |
| `karpathy-skills` | GitHub | `forrestchang/andrej-karpathy-skills` | Public repo, `autoUpdate: true`. |
| `knowledge-work-plugins` | GitHub | `anthropics/knowledge-work-plugins` | 16 Cowork plugins; only `productivity` and `cowork-plugin-management` are installed. |
| `ponytail` | Git URL | `https://github.com/DietrichGebert/ponytail.git` | Full `.git` URL, not `owner/repo`. |
| `vercel-vercel-plugin` | **Local directory** | `~/.cache/plugins/github.com-vercel-vercel-plugin` | ⚠️ Source must be rsynced from `vercel-marketplace-source/` first — see §5. |
| `agricidaniel-seo` | **Local directory** | `~/.claude/plugins/local-src/claude-seo` | ⚠️ Source must be rsynced from `claude-seo-source/` first — same pattern as Vercel. |

---

## 4. Restoration on a new Mac

`Tooling/restore.sh` step 6 does all of this. The manual equivalent:

### 4a. Restore the two local-directory sources FIRST

Registration fails if the directory is not already on disk.

```bash
mkdir -p ~/.cache/plugins ~/.claude/plugins/local-src
rsync -a Plugins/vercel-marketplace-source/ ~/.cache/plugins/github.com-vercel-vercel-plugin/
rsync -a Plugins/claude-seo-source/ ~/.claude/plugins/local-src/claude-seo/
```

### 4b. Register the marketplaces

Bare `owner/repo`, URL, or path — **never** a `github`/`git`/`directory` keyword (see §0).

```bash
claude plugin marketplace add obra/superpowers-marketplace
claude plugin marketplace add forrestchang/andrej-karpathy-skills
claude plugin marketplace add anthropics/knowledge-work-plugins
claude plugin marketplace add https://github.com/DietrichGebert/ponytail.git
claude plugin marketplace add ~/.cache/plugins/github.com-vercel-vercel-plugin
claude plugin marketplace add ~/.claude/plugins/local-src/claude-seo
```

`claude-plugins-official` is registered by Claude Code automatically.

### 4c. Install each plugin

```bash
claude plugin install figma@claude-plugins-official
claude plugin install vercel-plugin@vercel-vercel-plugin
claude plugin install superpowers@superpowers-marketplace
claude plugin install superpowers-chrome@superpowers-marketplace
claude plugin install superpowers-developing-for-claude-code@superpowers-marketplace
claude plugin install superpowers-lab@superpowers-marketplace
claude plugin install andrej-karpathy-skills@karpathy-skills
claude plugin install github@claude-plugins-official
claude plugin install ponytail@ponytail
claude plugin install youdotcom-agent-skills@claude-plugins-official
claude plugin install claude-seo@agricidaniel-seo
claude plugin install productivity@knowledge-work-plugins
claude plugin install cowork-plugin-management@knowledge-work-plugins
```

### 4d. Verify enabledPlugins block in `settings.json`

The shipped `../settings.json` enables 12 of the 13 (`vercel-plugin` is `false`). After copying `settings.json` into `~/.claude/`, no further action needed — Claude Code reads this on next session start.

```bash
claude plugin list   # should show 13 plugins installed, 12 enabled (vercel-plugin ships disabled)
```

---

## 5. The Vercel plugin gotcha — local-directory marketplace

On the source Mac, the Vercel marketplace was registered as a **local directory source**, not a GitHub source:

```json
"vercel-vercel-plugin": {
  "source": {
    "source": "directory",
    "path": "/Users/Dhiraj/.cache/plugins/github.com-vercel-vercel-plugin"
  }
}
```

This means the marketplace was pulled from a local cache, not the upstream repo. On a new Mac, that directory won't exist.

**Recovery options (in order of preference):**

1. **✅ Use the cache embedded in this kit (default).** The full 7.7 MB marketplace source is mirrored at `Plugins/vercel-marketplace-source/`. On the new Mac (set `$KIT_DIR` first — `cd "/path/to/Claude Agents and Skills (PORTABILITY KIT)" && export KIT_DIR="$PWD"`, per BOOTSTRAP.md §0):
   ```bash
   # 1. Place the source where the original Mac expected it
   mkdir -p ~/.cache/plugins
   rsync -a "$KIT_DIR/Plugins/vercel-marketplace-source/" \
            "$HOME/.cache/plugins/github.com-vercel-vercel-plugin/"

   # 2. Register the marketplace from that directory
   claude plugin marketplace add directory "$HOME/.cache/plugins/github.com-vercel-vercel-plugin"

   # 3. Install the plugin (this command then "just works")
   claude plugin install vercel-plugin@vercel-vercel-plugin
   ```

2. **Re-pull from upstream GitHub** — only needed if you want the latest version instead of the snapshotted one. Check Vercel's [current plugin docs](https://vercel.com/docs/claude) for the canonical install command. The marketplace slug will change — adjust the `enabledPlugins` key in `settings.json` to match, and update `known_marketplaces.json` in this folder.

3. **Skip** — defer the entire Vercel layer if you don't need it right now.

---

## 6. Plugin update / removal

```bash
# Update a single plugin
claude plugin update <name>@<marketplace>

# Update everything
claude plugin update --all

# Disable without removing
claude plugin disable <name>@<marketplace>   # also: edit settings.json enabledPlugins → false

# Remove
claude plugin remove <name>@<marketplace>
```

After any change, sync the snapshots in this folder (with `$KIT_DIR` pointing at this kit — `export KIT_DIR="$PWD"` from inside it):

```bash
cp ~/.claude/plugins/installed_plugins.json "$KIT_DIR/Plugins/"
cp ~/.claude/plugins/known_marketplaces.json "$KIT_DIR/Plugins/"
cp ~/.claude/settings.json "$KIT_DIR/"
```

---

## 7. Cowork (Claude Desktop) plugins — not in this folder

The product-management, marketing, sales, atlan, apollo, biorender, daloopa, etc. plugins surfaced via Claude Desktop / Cowork are **account-bound**, not in `installed_plugins.json`. They restore automatically on `claude login` on the new Mac. Their full list is in [../Connectors/README.md](../Connectors/README.md).

If you ever need to capture the Cowork plugin set verbatim, dump `~/.claude/mcp-needs-auth-cache.json` — it lists every `plugin:<name>:<connector>` ever auth-prompted.

---

## 8. File inventory in this folder

```
Plugins/
├── README.md                       ← this file
├── installed_plugins.json          ← snapshot of ~/.claude/plugins/installed_plugins.json (13 plugins)
├── known_marketplaces.json         ← snapshot of ~/.claude/plugins/known_marketplaces.json (4 marketplaces)
└── vercel-marketplace-source/      ← 7.7 MB mirror of ~/.cache/plugins/github.com-vercel-vercel-plugin/
                                      (the actual marketplace source — see §5 option 1)
```
