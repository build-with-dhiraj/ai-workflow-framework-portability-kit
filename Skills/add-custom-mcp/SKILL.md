---
name: add-custom-mcp
description: >-
  Discover the best community MCP server on GitHub/npm for any service,
  install it into Claude Code via the `claude mcp` CLI, wire authentication
  from existing local credentials, and verify tools work. Use when the user
  asks to add, install, connect, or activate a custom MCP server or connector
  for any tool (GitLab, Jira, Slack, Asana, etc.) in Claude Code.
---

# Add Custom MCP to Claude Code

End-to-end workflow: **research → pick winner → configure auth → install → verify**.

Claude Code manages MCP servers through the `claude mcp` CLI — never hand-edit
`~/.claude.json` or a project's `.mcp.json` directly; the CLI keeps scope and
JSON structure correct and merges idempotently on its own.

## When to use

- User wants a new MCP server for any service
- User says "add MCP for X", "connect X to Claude Code", "find best X MCP"
- Replacing or upgrading an existing MCP entry

## Execution checklist

Copy and track:

```
- [ ] 1. Scope — service name, read vs write, local/user/project config
- [ ] 2. Discover — GitHub + npm search, score candidates, pick winner
- [ ] 3. Auth — find existing local credentials; never invent secrets
- [ ] 4. Install — `claude mcp add` (idempotent by construction)
- [ ] 5. Verify — `claude mcp list`/`get`, ToolSearch, one live tool call
- [ ] 6. Report — winner repo, config location, verification result
```

---

## Step 1 — Scope

Ask or infer:

| Question | Default |
|----------|---------|
| Which service? | From user message |
| Read-only or write? | **Read-only** unless user needs mutations |
| Config scope | **local** (this project only) unless user wants it everywhere (`user`) or shared with a team via git (`project`) |

**Before adding:** run `claude mcp list` — check if the server already exists under a similar key; `claude mcp add` on an existing name updates it, it won't duplicate.

**Scope carries real consequences** — see [reference.md](reference.md) for the full comparison, but in short: `project` scope writes a `.mcp.json` meant to be committed to git, so secrets must never go there directly (use `${env:VAR}` references instead).

---

## Step 2 — Discover best GitHub repo

Run **in parallel**:

1. **GitHub search** (`gh search repos "<service> mcp server" --sort=stars` or WebSearch): sort by stars
2. **Web search**: `"<service> MCP server 2026"`
3. **npm search** (if applicable): `npm search "<service> mcp"` or check `https://api.npmjs.org/downloads/point/last-month/<pkg>`

### Scoring rubric (pick highest total; cite numbers)

| Signal | Weight | How to measure |
|--------|--------|-----------------|
| GitHub stars | 3× | Primary popularity signal |
| Forks | 1× | Community adoption |
| Recency | 2× | `updated_at` within 90 days = full points |
| npm downloads (30d) | 2× | `curl https://api.npmjs.org/downloads/point/last-month/<pkg>` |
| Claude/MCP docs | 2× | Dedicated setup guide or `claude`/`mcp` in README |
| Official vs community | — | Prefer **official** only if user has the required tier/license |

**Disqualify:** archived repos, no commits in 6+ months, README says "unmaintained".

**Present to user:** winner + 2 runners-up in a short table, then proceed with winner unless user overrides.

Always re-run discovery — rankings change.

---

## Step 3 — Authentication

**Rule:** reuse existing credentials. Never commit secrets to git repos. Never print tokens in chat.

### Credential lookup order

1. **Already configured** — `claude mcp list` for a similar service, same env var pattern
2. **`~/.git-credentials`** — parse host-specific PAT (see [reference.md](reference.md) for the parser)
3. **Shell env** — `env | rg -i '<SERVICE>_TOKEN|API_KEY'` (names only, not values)
4. **`~/.env` / project `.env`** — only if user owns that path; git-ignored
5. **OAuth** — if the server supports it and no PAT exists, use `claude mcp login <name>` after adding the server as an HTTP/SSE endpoint; user completes the browser flow

**Read-only:** pass the server's read-only env flag when available (e.g. `GITLAB_READ_ONLY_MODE=true`).

**Token diet:** for large servers (100+ tools), set toolset/allowlist env vars if the server supports them — Claude Code already defers tool schemas via ToolSearch, but a smaller server-side toolset still saves setup time and avoids noisy tool lists.

---

## Step 4 — Install via `claude mcp add`

### Read the winner's README first

Extract the exact command, required env vars, and whether it's stdio or HTTP/SSE.

### stdio server

```bash
claude mcp add <name> -s local -e API_KEY=<value> -- npx -y <package>@<pinned-version>
```

- Pin the version (not `@latest`) for reproducibility.
- Use `-s user` instead of `-s local` for a server you want in every project.
- Use `-s project` only when the team should share it — commit the resulting `.mcp.json`, and reference secrets as `${env:VAR}` rather than inline values.

### HTTP/SSE (remote) server

```bash
claude mcp add --transport http <name> https://example.com/mcp -H "Authorization: Bearer ${MY_TOKEN}"
```

Then, if the server needs an interactive OAuth flow instead of a static header:

```bash
claude mcp login <name>
```

### One-shot JSON form (equivalent, useful when copying a config block from a README)

```bash
claude mcp add-json <name> '{"command":"npx","args":["-y","<package>@<version>"],"env":{"API_KEY":"..."}}'
```

### Importing from Claude Desktop

If the user already has this server configured in Claude Desktop:

```bash
claude mcp add-from-claude-desktop
```

---

## Step 5 — Verify

1. **Connection status:** `claude mcp get <name>` or `claude mcp list` — look for `✔ Connected`. Treat `! Connected · tools fetch failed` and `✘ Failed to connect` as failures, not partial success — dig into the server's logs/README rather than reporting it as installed.
2. **Load tool schemas:** in a live session, `ToolSearch` with `"select:<known-tool-name>"` or a keyword for the service — schemas are deferred until requested.
3. **Live call:** invoke one **read-only** tool (list projects, get me, health check) and confirm it returns real data, not an auth/connection error.

---

## Step 6 — Report

```markdown
## MCP installed: <service>

**Winner:** [<repo>](url) — ⭐ X stars, npm `<pkg>@<version>`, updated <date>
**Command:** `claude mcp add ...` (scope: local/user/project)
**Auth:** <source, e.g. ~/.git-credentials gitlab.com PAT> (read-only)
**Verified:** `<tool_name>` → <one-line result summary>

**Try next:** "<example prompt>"
```

Do **not** include secret values in the report.

---

## Reference

- [Scoring details, scope comparison, credential parsers](reference.md)
- [GitLab install example + generic flow](examples.md)
