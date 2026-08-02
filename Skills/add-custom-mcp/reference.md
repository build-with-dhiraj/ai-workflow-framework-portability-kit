# Add Custom MCP — Reference

## `claude mcp` scope comparison

| Scope | Flag | Where it's written | Shared? | Secrets rule |
|-------|------|---------------------|---------|--------------|
| Local (default) | `-s local` | this working directory only, in Claude Code's own state | No — just you, this repo | Fine to inline (still local-only, not committed) |
| User | `-s user` | `~/.claude.json`, global across all projects | Just you, everywhere | Fine to inline |
| Project | `-s project` | `.mcp.json` in repo root | **Yes — meant to be committed to git** | Never inline; use `${env:VAR}` and require teammates to export it |

Never hand-edit `~/.claude.json` or a project `.mcp.json` directly — always go
through `claude mcp add` / `add-json` / `remove` so the CLI keeps the
structure and any existing entries intact.

## GitHub/npm search queries

```
"<service> mcp server"
"<service> model context protocol"
```

Add `stars:>20` once you know the space has mature options.

## npm download check

```bash
curl -s "https://api.npmjs.org/downloads/point/last-month/@scope%2Fpackage"
```

URL-encode `/` as `%2F`.

## Credential parsers

### git-credentials (multi-host)

```python
import re
from pathlib import Path

def pat_for_host(host: str) -> str | None:
    for line in Path("~/.git-credentials").expanduser().read_text().splitlines():
        if host not in line:
            continue
        m = re.match(rf"https?://(?:[^:@/]+):([^@]+)@{re.escape(host)}", line.strip())
        if m:
            return m.group(1)
    return None
```

### Shell env grep (names only, never print values)

```bash
env | rg -i '<SERVICE>_TOKEN|API_KEY' | cut -d= -f1
```

## Common env var names by service

| Service | Typical vars |
|---------|--------------|
| GitLab | `GITLAB_PERSONAL_ACCESS_TOKEN`, `GITLAB_API_URL` |
| GitHub | `GITHUB_PERSONAL_ACCESS_TOKEN` |
| Notion | `NOTION_API_KEY` |
| Linear | OAuth via remote URL — no PAT needed, use `claude mcp login` |
| Slack | `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID` |

Always defer to the chosen repo's README for the authoritative list.

## Security

- Never write tokens into project repos, especially under `project` scope `.mcp.json`
- Prefer `${env:VAR}` over inline secrets whenever the user already exports the var, and *require* it for `project` scope
- Use read-only mode + minimal toolsets for PM/review workflows

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `claude mcp list` shows `✘ Failed to connect` | Check command/args are correct; run the command manually in a terminal to see the raw error |
| `! Connected · tools fetch failed` | Server started but tool discovery failed — check server logs/README for a startup delay or missing required env var |
| Tools not visible in session | They're deferred — call `ToolSearch` with the tool name or a keyword before invoking |
| 401 from API | Re-check PAT scopes vs the server's README |
| OAuth stuck | `claude mcp logout <name>` then `claude mcp login <name>` again |
