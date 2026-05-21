# Plugins — Roster & Restoration

Plugins are bundled packages that ship a curated mix of skills, agents, and MCP servers. They're managed via the Claude Code `plugin` CLI and registered marketplaces. This folder snapshots **which plugins were installed**, **which marketplaces they came from**, and how to restore them on a new Mac.

> **Where the live state lives on the Mac:** `~/.claude/plugins/installed_plugins.json` + `~/.claude/plugins/known_marketplaces.json` + `~/.claude/settings.json` (`enabledPlugins` section).
> **Restoration:** the snapshot files in this folder + the install commands below.

---

## 1. The two kinds of plugin you have

### 1a. Local Claude Code plugins (8) — fully captured here

These show up in `installed_plugins.json` and are managed by the `claude plugin` CLI. They are the authoritative scope of "what Claude Code on this Mac has installed."

### 1b. Account / Cowork plugins — captured by reference

These show up in `~/.claude/mcp-needs-auth-cache.json` with `plugin:<plugin-name>:<connector-name>` keys but **don't** appear in `installed_plugins.json`. They were installed via Claude Desktop / Cowork, which is account-bound — they reattach on `claude login`. See [../Connectors/README.md](../Connectors/README.md) for the inventory.

---

## 2. Local plugins — what's installed (8)

| Plugin | Marketplace | Version | Scope | What it ships |
|---|---|---|---|---|
| `figma` | `claude-plugins-official` | 2.0.2 | project | Figma MCP server (`use_figma`) + 5 Figma skills + an MCP for plugin authentication |
| `vercel-plugin` | `vercel-vercel-plugin` | 0.24.0 | project | Vercel CLI/API wrapper + 29 Vercel skills (ai-sdk, nextjs, deploy, env, workflow, shadcn, etc.) + Vercel MCP |
| `superpowers` | `superpowers-marketplace` | 5.1.0 | project | ~14 process skills: brainstorming, writing-plans, executing-plans, subagent-driven-development, dispatching-parallel-agents, verification-before-completion, using-git-worktrees, finishing-a-development-branch, requesting-code-review, receiving-code-review, systematic-debugging, test-driven-development, writing-skills, context-kernel |
| `superpowers-chrome` | `superpowers-marketplace` | 1.12.0 | user | `browsing` skill + Chrome DevTools Protocol MCP (`use_browser`) |
| `superpowers-developing-for-claude-code` | `superpowers-marketplace` | 0.3.1 | user | `working-with-claude-code`, `developing-claude-code-plugins` |
| `superpowers-lab` | `superpowers-marketplace` | 0.4.0 | user | `slack-messaging`, `windows-vm`, `mcp-cli`, `finding-duplicate-functions`, `using-tmux-for-interactive-commands` |
| `andrej-karpathy-skills` | `karpathy-skills` | 1.0.0 | user | `karpathy-guidelines` (behavioral coding guardrails) |
| `github` | `claude-plugins-official` | unknown | user | GitHub-related slash commands and helpers |

**Two skill-precedence notes (also in [../CLAUDE.md §4](../CLAUDE.md)):**

- `superpowers:systematic-debugging` is shadowed by local `diagnose` (Mattpocock). Use `diagnose`.
- `superpowers:test-driven-development` is shadowed by local `tdd` (Mattpocock). Use `tdd`.
- `superpowers:writing-skills` is shadowed by local `write-a-skill` (Mattpocock). Use `write-a-skill`.

---

## 3. Marketplaces (4) — where the plugins come from

Snapshot in `known_marketplaces.json` next to this README.

| Marketplace | Source type | Source | Notes |
|---|---|---|---|
| `claude-plugins-official` | GitHub | `anthropics/claude-plugins-official` | Default — registered by Claude Code at install time. No action needed. |
| `vercel-vercel-plugin` | **Local directory** | `/Users/pw/.cache/plugins/github.com-vercel-vercel-plugin` | ⚠️ On a new Mac this directory doesn't exist — see §5 for restore options. |
| `superpowers-marketplace` | GitHub | `obra/superpowers-marketplace` | Public repo. |
| `karpathy-skills` | GitHub | `forrestchang/andrej-karpathy-skills` | Public repo. |

---

## 4. Restoration on a new Mac

### 4a. Register the marketplaces

```bash
# superpowers + karpathy — both from public GitHub
claude plugin marketplace add github obra/superpowers-marketplace
claude plugin marketplace add github forrestchang/andrej-karpathy-skills

# vercel-vercel-plugin (special — see §5)
# Skip for now; install vercel-plugin via the upstream GitHub source as a workaround.
```

`claude-plugins-official` is registered by Claude Code automatically.

### 4b. Install each plugin

```bash
claude plugin install figma@claude-plugins-official
claude plugin install vercel-plugin@vercel-vercel-plugin    # see §5 if this fails
claude plugin install superpowers@superpowers-marketplace
claude plugin install superpowers-chrome@superpowers-marketplace
claude plugin install superpowers-developing-for-claude-code@superpowers-marketplace
claude plugin install superpowers-lab@superpowers-marketplace
claude plugin install andrej-karpathy-skills@karpathy-skills
claude plugin install github@claude-plugins-official
```

### 4c. Verify enabledPlugins block in `settings.json`

The shipped `../settings.json` has these eight plugins set to `true` under `enabledPlugins`. After copying `settings.json` into `~/.claude/`, no further action needed — Claude Code reads this on next session start.

```bash
claude plugin list   # should show 8 plugins, all enabled
```

---

## 5. The Vercel plugin gotcha — local-directory marketplace

On the source Mac, the Vercel marketplace was registered as a **local directory source**, not a GitHub source:

```json
"vercel-vercel-plugin": {
  "source": {
    "source": "directory",
    "path": "/Users/pw/.cache/plugins/github.com-vercel-vercel-plugin"
  }
}
```

This means the marketplace was pulled from a local cache, not the upstream repo. On a new Mac, that directory won't exist.

**Recovery options (in order of preference):**

1. **✅ Use the cache embedded in this kit (default).** The full 7.7 MB marketplace source is mirrored at `Plugins/vercel-marketplace-source/`. On the new Mac:
   ```bash
   # 1. Place the source where the original Mac expected it
   mkdir -p ~/.cache/plugins
   rsync -a "/Users/pw/Claude Agents and Skills/Plugins/vercel-marketplace-source/" \
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

After any change, sync the snapshots in this folder:

```bash
cp ~/.claude/plugins/installed_plugins.json "/Users/pw/Claude Agents and Skills/Plugins/"
cp ~/.claude/plugins/known_marketplaces.json "/Users/pw/Claude Agents and Skills/Plugins/"
cp ~/.claude/settings.json "/Users/pw/Claude Agents and Skills/"
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
├── installed_plugins.json          ← snapshot of ~/.claude/plugins/installed_plugins.json (8 plugins)
├── known_marketplaces.json         ← snapshot of ~/.claude/plugins/known_marketplaces.json (4 marketplaces)
└── vercel-marketplace-source/      ← 7.7 MB mirror of ~/.cache/plugins/github.com-vercel-vercel-plugin/
                                      (the actual marketplace source — see §5 option 1)
```
