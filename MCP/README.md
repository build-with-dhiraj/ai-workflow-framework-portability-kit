# MCP Servers — Roster & Restoration

MCP (Model Context Protocol) servers are the "tools" layer of the architecture — they give agents capabilities like *send a Slack message*, *query Supabase*, *read Gmail*. Some live in local config files; others are bound to your Claude account; others ship inside plugins. This folder documents all three.

> **Where the local file lives on the Mac:** `~/.claude/mcp.json` (HTTP/stdio servers you configured manually).
> **Restoration:** copy `mcp.template.json` here back to `~/.claude/mcp.json` and replace the `REDACTED_*` tokens.

---

## 1. The three layers of MCP

The same protocol, three management surfaces. Knowing which is which determines what survives a Mac replacement.

| Layer | Where configured | Survives Mac wipe? | What lives in it on your account |
|---|---|---|---|
| **Local MCP** | `~/.claude/mcp.json` | ⚠️ Only the file — secrets must be re-pasted | `n8n` (HTTP, JWT auth) |
| **Plugin-bundled MCP** | Inside `~/.claude/plugins/cache/<plugin>/` | ✅ Auto-restored when plugin is reinstalled | `figma`, `vercel`, `chrome` (Superpowers Chrome) |
| **Claude Account Connectors** | claude.ai → Settings → Connectors (or Claude Desktop UI) | ✅ Auto-attached on login | Gmail, Calendar, Drive, Scholar Gateway, Stitch, Figma, Atlassian Rovo, +many Cowork plugin connectors |

See [../Connectors/README.md](../Connectors/README.md) for the deep dive on the third layer — that's where the bulk of your integrations actually live.

---

## 2. Local MCP servers (`~/.claude/mcp.json`)

Currently one server. The full registry is in `mcp.template.json` next to this README.

| Server | Type | Auth | Purpose |
|---|---|---|---|
| `n8n` | HTTP | Bearer JWT (REDACTED in template) | n8n cloud automation — fires workflows from Claude |

**Restoration:**

```bash
# 1. Open the template, paste the live JWT (it's in your password manager)
$EDITOR "/Users/pw/Claude Agents and Skills/MCP/mcp.template.json"

# 2. Copy into place
cp "/Users/pw/Claude Agents and Skills/MCP/mcp.template.json" ~/.claude/mcp.json
```

**Adding more:** local MCPs are JSON entries in this file with this shape:

```json
{
  "mcpServers": {
    "<server-name>": {
      "type": "http" | "stdio",
      "url": "https://...",                    // for http
      "command": "..." , "args": [...],        // for stdio
      "headers": { "Authorization": "Bearer ..." }
    }
  }
}
```

---

## 3. Plugin-bundled MCP servers

These come with installed Claude Code plugins. Reinstall the plugin and the MCP server reattaches. See [../Plugins/README.md](../Plugins/README.md) for plugin reinstall commands.

| Plugin | MCP server name (tool prefix) | What it does |
|---|---|---|
| `figma@claude-plugins-official` | `mcp__plugin_figma_figma__` | Figma Plugin API (`authenticate`, `complete_authentication`) — bridge to Figma write actions via `use_figma` |
| `vercel-plugin@vercel-vercel-plugin` | `mcp__plugin_vercel-plugin_vercel__` | Vercel API (`authenticate`, `complete_authentication`) |
| `superpowers-chrome@superpowers-marketplace` | `mcp__plugin_superpowers-chrome_chrome__` | Chrome DevTools Protocol — `use_browser` for direct browser control |

**Restoration:** automatic once the parent plugin is reinstalled.

---

## 4. Claude Account MCP servers (a.k.a. Connectors)

These are configured at **claude.ai → Settings → Connectors** or in the Claude Desktop UI. They're bound to your Anthropic account, not to this Mac. **They reattach automatically when you `claude login` on the new Mac.** No file restoration needed.

Inventory snapshot (from `~/.claude/mcp-needs-auth-cache.json`):

### 4a. Direct claude.ai connectors

| Connector | MCP ID | Notes |
|---|---|---|
| `claude.ai Gmail` | `mcpsrv_016sNCMZoLESLiQHjiryUpaH` | OAuth re-auth needed on first use |
| `claude.ai Google Calendar` | `mcpsrv_01CfApRFxbDeRyJ1aQ7ihBpC` | OAuth re-auth needed |
| `claude.ai Google Drive` | `mcpsrv_01Dk8zbqgjGxPShv1wrzYJCe` | OAuth re-auth needed |
| `claude.ai Scholar Gateway` | `mcpsrv_01EkYkgVpoDaW97wm3B4VVsf` | Scholarly article search |
| `claude.ai Stitch` | `mcpsrv_01BAkYSATSHgkKerDye1eLPt` | Google Stitch (UI design AI) |
| `claude.ai Figma` | `mcpsrv_01PGsEKLGpyRjZiJjKzA1xGS` | OAuth re-auth needed |
| `claude.ai Atlassian Rovo` | `mcpsrv_01BfApsvoPvdy8BK8bQbzw7F` | Atlassian-wide search/automate |

### 4b. Account-bound MCP servers seen in this session

These appeared as `mcp__<hash>__*` tools in the deferred-tools list, meaning they're connected to your account and discoverable:

| Tool prefix in session | Probable connector | Tool count |
|---|---|---|
| `mcp__0d39b089-...` | Granola (meeting transcripts, `query_granola_meetings`) | 6 |
| `mcp__0fb48f1e-...` | Scholar Gateway (articles, citations) | 7 |
| `mcp__13d28a7f-...` | Supabase (apply_migration, list_projects, execute_sql, etc.) | 32 |
| `mcp__2295aecb-...` | Vercel (deployments, runtime logs, toolbar threads) | 22 |
| `mcp__2f85f1b4-...` | Gmail (drafts, threads, labels) | 11 |
| `mcp__6733926c-...` | Google Drive (read_file, search_files, list_recent_files) | 8 |
| `mcp__c6399901-...` | Slack (messages, canvases, channels) | 20 |
| `mcp__Metabase__` | Metabase (BI dashboards) | 6 |
| `mcp__notebooklm__` | NotebookLM (notebooks, sources, studio artifacts) | 40+ |
| `mcp__pinecone__` | Pinecone (vector DB, cascading search) | 11 |
| `mcp__reddit-search__` | Reddit (search, posts, comments) | 17 |
| `mcp__repomix__` | Repomix (codebase packing) | 7 |
| `mcp__chrome-devtools__` | Anthropic Chrome DevTools | 30+ |
| `mcp__dart-mcp-server__` | Dart / Flutter dev tools | 26 |
| `mcp__zapier__` | Zapier (Confluence, Gmail subactions, etc.) | 17 |
| `mcp__stitch__`, `mcp__stitch-gemini-build__` | Google Stitch (design + build) | 14 + 3 |
| `mcp__lennybot-live__` | Lenny's Newsletter assistant | 1 |
| `mcp__mcp-registry__` | MCP registry (discover/install connectors) | 3 |
| `mcp__scheduled-tasks__` | Scheduled task runner | 3 |
| `mcp__google-drive__` | Google Drive (alternative client) | 8 |
| `mcp__slack__` | Slack (alternative client — workspace search, usergroups) | 12 |
| `mcp__Claude_Preview__` | Claude Preview (Vercel-hosted page previewer) | 13 |
| `mcp__Claude_in_Chrome__` | Claude in Chrome extension | 28 |
| `mcp__Control_Chrome__` | Control Chrome (browser automation) | 9 |
| `mcp__ccd_directory__`, `mcp__ccd_session_mgmt__` | Claude Code Desktop session/directory mgmt | 4 |

> **Why two Slack servers / two Google Drive servers / two Chrome controllers?** Different connector vendors expose overlapping capabilities. Pick one per use case — typically the one with the richest tool surface (e.g., `mcp__c6399901-...` for Slack messaging; `mcp__slack__` for workspace admin like usergroups).

---

## 5. Restoration order on a new Mac

1. **Local MCP** — Copy `mcp.template.json` → `~/.claude/mcp.json`, paste secrets.
2. **Plugin-bundled MCP** — Reinstall plugins per [../Plugins/README.md](../Plugins/README.md). MCPs reattach automatically.
3. **Account connectors** — Run `claude login`. The first time you invoke a connector that needs OAuth (e.g., Gmail), Claude will prompt you to re-authorize in the browser.
4. **Verify** — In a Claude Code session, ask: *"list all available MCP tool prefixes."* You should see all `mcp__*` namespaces from the inventory above.

---

## 6. Anti-patterns

- ❌ Storing JWT/OAuth secrets in this folder — they're redacted in the template for a reason.
- ❌ Trying to migrate account connectors via file copy — they're not in any local file; they live on the Anthropic side.
- ❌ Re-creating an `n8n` MCP entry from memory of the URL — the JWT is required; pull from password manager.
- ❌ Confusing the Slack/Drive/Chrome duplicates — keep notes per-project on which you're using.

---

## 7. Adding a new MCP server later

If you discover an MCP server you want, the path depends on its type:

| Type | Path |
|---|---|
| Public MCP via Claude Desktop | claude.ai → Settings → Connectors → Add |
| MCP from a plugin marketplace | `claude plugin install <plugin>@<marketplace>` |
| Self-hosted HTTP MCP | Edit `~/.claude/mcp.json` |
| Self-hosted stdio MCP | Edit `~/.claude/mcp.json` with `command`/`args` |

If you add an HTTP/stdio one to `~/.claude/mcp.json`, mirror it in this folder's `mcp.template.json` (with secrets redacted) so a future restoration is complete.
