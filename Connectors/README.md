# Connectors — Account-Bound Integrations

Connectors are integrations managed at the **Anthropic account level** rather than per-machine. They're configured at *claude.ai → Settings → Connectors* or via Claude Desktop / Cowork. Under the hood they are MCP servers — but you don't manage them through `~/.claude/mcp.json`. Their auth tokens live on Anthropic's side, so they reattach to your account on any new Mac.

> **The headline:** **Connectors survive Mac replacement automatically.** Run `claude login` on the new Mac and they reappear. No file restoration needed. This folder exists to **inventory** what you had, in case you need to verify everything reattached.

---

## 1. Connectors vs. local MCP — what's the difference?

| Dimension | Local MCP (`mcp.json`) | Plugin-bundled MCP | Account Connector |
|---|---|---|---|
| **Where you add it** | Edit `~/.claude/mcp.json` | `claude plugin install` | claude.ai / Claude Desktop UI |
| **Where the config lives** | Local file | Plugin cache directory | Anthropic backend |
| **Auth surface** | You paste JWT/Bearer | OAuth via plugin flow | OAuth via claude.ai |
| **Survives Mac wipe?** | Only if file is backed up | Auto (when plugin reinstalls) | Auto (account-bound) |
| **Visible in this session as** | `mcp__<name>__*` | `mcp__plugin_<plugin>_<server>__*` | `mcp__<hash>__*` or `mcp__<name>__*` |

If you can see it as a tool in a Claude Code session but it's *not* in any local file, it's a connector.

---

## 2. Direct claude.ai connectors

These were added directly in *claude.ai → Settings → Connectors*. From `~/.claude/mcp-needs-auth-cache.json`:

| Connector | MCP server ID | OAuth scope | What it gives Claude |
|---|---|---|---|
| `claude.ai Gmail` | `mcpsrv_016sNCMZoLESLiQHjiryUpaH` | Gmail read + write | Read threads, draft/send, manage labels |
| `claude.ai Google Calendar` | `mcpsrv_01CfApRFxbDeRyJ1aQ7ihBpC` | Calendar read | Inspect events, free/busy |
| `claude.ai Google Drive` | `mcpsrv_01Dk8zbqgjGxPShv1wrzYJCe` | Drive read | Search, read files |
| `claude.ai Scholar Gateway` | `mcpsrv_01EkYkgVpoDaW97wm3B4VVsf` | none (public corpus) | Scholarly article search & metadata |
| `claude.ai Stitch` | `mcpsrv_01BAkYSATSHgkKerDye1eLPt` | Google Stitch | AI-assisted UI design |
| `claude.ai Figma` | `mcpsrv_01PGsEKLGpyRjZiJjKzA1xGS` | Figma read/write | Inspect designs, generate code |
| `claude.ai Atlassian Rovo` | `mcpsrv_01BfApsvoPvdy8BK8bQbzw7F` | Atlassian Cloud | Jira/Confluence search + actions |

---

## 3. Cowork / Claude Desktop plugin connectors

The Cowork (Claude Desktop) plugin layer surfaces dozens of vendor integrations. They appear in `~/.claude/mcp-needs-auth-cache.json` as `plugin:<plugin-name>:<connector>`. Each was OAuth-prompted at the timestamp recorded.

### 3a. Product Management plugin

| Connector | Tool surface |
|---|---|
| Linear | Issues, projects, cycles |
| Notion | Pages, databases |
| Monday.com | Boards, items |
| Intercom | Conversations, contacts |
| Slack | Messages, channels |
| Atlassian | Jira, Confluence |
| Amplitude (US + EU) | Product analytics |
| Fireflies | Meeting transcripts |
| Pendo | Product analytics |
| Figma | Designs |
| ClickUp | Tasks |

### 3b. Marketing plugin

| Connector | Tool surface |
|---|---|
| Canva | Design assets |
| Ahrefs | SEO data |
| Klaviyo | Email marketing |
| Supermetrics | Marketing data aggregation |

### 3c. Sales plugin

| Connector | Tool surface |
|---|---|
| Microsoft 365 | Email, calendar, files |
| Close | CRM |

### 3d. Enterprise Search plugin

| Connector | Tool surface |
|---|---|
| Guru | Knowledge base |

### 3e. Bio-Research plugin

| Connector | Tool surface |
|---|---|
| BioRender | Biology illustrations |
| Wiley | Scientific publishing |
| Synapse | Research data sharing |

### 3f. Data & Analytics plugins

| Connector | Tool surface |
|---|---|
| Hex (`plugin:data:hex`) | Data notebooks |
| Daloopa | Financial data |
| Atlan | Data catalog |
| S&P Global | Financial intelligence |
| Apollo | Sales intelligence / GraphQL |
| Common Room | Community intelligence |

### 3g. Design & Build plugins

| Connector | Tool surface |
|---|---|
| Sanity | Headless CMS |
| Miro | Whiteboards |
| Adspirer (Ads Agent) | Ad campaign mgmt |

### 3h. Database plugins

| Connector | Tool surface |
|---|---|
| Prisma Remote | Prisma Postgres |
| PlanetScale | MySQL-compatible serverless DB |

---

## 4. Account-bound MCPs surfaced in this session

These appeared as `mcp__<hash>__*` or `mcp__<name>__*` tools in the deferred-tools list — meaning the live account had them connected at session start. They're either claude.ai connectors (above) or independent MCP servers attached to the account.

| Tool prefix | Connector | Reattaches on login? |
|---|---|---|
| `mcp__0d39b089-...` | Granola (meeting transcripts) | ✅ |
| `mcp__0fb48f1e-...` | Scholar Gateway (articles) | ✅ |
| `mcp__13d28a7f-...` | Supabase | ✅ |
| `mcp__2295aecb-...` | Vercel | ✅ |
| `mcp__2f85f1b4-...` | Gmail | ✅ (OAuth re-prompt) |
| `mcp__6733926c-...` | Google Drive | ✅ (OAuth re-prompt) |
| `mcp__c6399901-...` | Slack | ✅ (OAuth re-prompt) |
| `mcp__Metabase__` | Metabase | ✅ |
| `mcp__notebooklm__` | NotebookLM | ✅ (run `nlm login` for CLI parity) |
| `mcp__pinecone__` | Pinecone | ✅ |
| `mcp__reddit-search__` | Reddit (read-only safety boundary) | ✅ |
| `mcp__repomix__` | Repomix | ✅ |
| `mcp__chrome-devtools__` | Anthropic Chrome DevTools | ✅ |
| `mcp__dart-mcp-server__` | Dart / Flutter dev tools | ✅ |
| `mcp__zapier__` | Zapier (Confluence, Gmail sub-actions) | ✅ |
| `mcp__stitch__`, `mcp__stitch-gemini-build__` | Google Stitch | ✅ |
| `mcp__lennybot-live__` | Lenny's Newsletter | ✅ |
| `mcp__mcp-registry__` | MCP registry (for discovering new MCPs) | ✅ |
| `mcp__scheduled-tasks__` | Scheduled tasks | ✅ |
| `mcp__google-drive__` | Google Drive (alt client) | ✅ |
| `mcp__slack__` | Slack (alt client — workspace admin) | ✅ |
| `mcp__Claude_Preview__` | Claude Preview (Vercel page previewer) | ✅ |
| `mcp__Claude_in_Chrome__` | Claude in Chrome extension | ✅ |
| `mcp__Control_Chrome__` | Control Chrome | ✅ |
| `mcp__ccd_directory__`, `mcp__ccd_session_mgmt__` | Claude Code Desktop directory + sessions | ✅ |

---

## 5. Restoration on a new Mac

1. **Install Claude Desktop / Cowork** if you use them — they're separate from Claude Code CLI.
2. **`claude login`** — your Anthropic account state, including all account-bound connectors, reattaches.
3. **OAuth re-prompts** — on first use, any connector with an OAuth token will pop a browser flow. Common ones: Gmail, Drive, Calendar, Figma, Atlassian, Slack. Approve to re-bind.
4. **Verify** — start a Claude Code session and ask:
   *"List all currently available MCP tool prefixes."* The set should match §4 above. If something is missing, open claude.ai → Settings → Connectors and re-add it.

---

## 6. Discovering new connectors

The `mcp-registry` MCP (already account-bound) provides:

- `search_mcp_registry` — search the official registry
- `list_connectors` — list available connectors
- `suggest_connectors` — recommend based on context

Use it instead of guessing connector names from memory.

---

## 7. Anti-patterns

- ❌ Trying to back up connector OAuth tokens — they're not local; they live on Anthropic's side.
- ❌ Pasting an OAuth client_secret into `mcp.json` — that's for **local** MCP servers; connectors don't work that way.
- ❌ Duplicating a connector both as a local MCP and as an account connector — pick one. If both exist, the tool names will collide and Claude won't know which to call.
- ❌ Assuming `installed_plugins.json` captures Cowork plugins — it doesn't. Cowork plugins live entirely on the account side; this folder's README is the only local record.

---

## 8. What's actually in this folder

```
Connectors/
└── README.md   ← this file (no other files — connectors aren't stored as local files)
```

The inventory above IS the recovery kit for this layer. Bring it up on the new Mac, walk through §5, and you're done.
