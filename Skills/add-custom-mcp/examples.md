# Add Custom MCP — Examples

## Example 1: GitLab (reference run)

**User:** "Add GitLab MCP, use my existing PAT"

### Discovery result

| Repo | Stars | npm 30d | Updated |
|------|-------|---------|---------|
| **zereight/gitlab-mcp** | 1756 | 407K | Jul 2026 |
| yoda-digital/mcp-gitlab-server | 59 | 2K | Jul 2026 |
| structured-world/gitlab-mcp | 5 | 9K | Jun 2026 |

### Install command (token parsed from `~/.git-credentials`, not printed)

```bash
claude mcp add gitlab -s user \
  -e GITLAB_PERSONAL_ACCESS_TOKEN="<from ~/.git-credentials gitlab.com>" \
  -e GITLAB_API_URL="https://gitlab.com/api/v4" \
  -e GITLAB_READ_ONLY_MODE="true" \
  -e GITLAB_TOOLSETS="projects,merge_requests,pipelines,repository" \
  -- npx -y @zereight/mcp-gitlab@2.1.29
```

### Verify

```
$ claude mcp get gitlab
✔ Connected

# in a live session
ToolSearch("select:mcp__gitlab__list_projects")
mcp__gitlab__list_projects(membership=true, search="research-svc")
→ acme-org/engineering/research-svc
```

---

## Example 2: Unknown service (generic flow)

**User:** "Add MCP for Asana"

1. Search GitHub/npm → `"asana mcp server"`, sort by stars
2. `claude mcp list` — check if an `asana` entry already exists (may be OAuth remote — don't duplicate)
3. If adding a community stdio server: read its README, pin the npm version
4. Auth: check for an Asana PAT in `~/.git-credentials`/env, or set it up as HTTP + OAuth and use `claude mcp login asana`
5. Verify with a read-only tool (e.g. list workspaces)

```bash
# PAT case
claude mcp add asana -s user -e ASANA_ACCESS_TOKEN=<token> -- npx -y <winning-package>@<version>

# OAuth remote case
claude mcp add --transport http asana https://mcp.asana.com/mcp
claude mcp login asana
```

---

## Example 3: Project-shared scope

**User:** "Add Jira MCP for this repo, shared with the team"

```bash
claude mcp add jira -s project \
  -e JIRA_API_TOKEN='${env:JIRA_API_TOKEN}' \
  -- npx -y <winning-jira-mcp-package>@<version>
```

This writes `.mcp.json` in the repo root. Because it's `project` scope, it's
meant to be committed — the token is a `${env:VAR}` reference, never an
inline value, so each teammate supplies their own via their shell env.

---

## Example prompts after install

| Service | Test prompt |
|---------|--------------|
| GitLab | "List open MRs on research-svc" |
| GitHub | "Show my open PRs in org/repo" |
| Notion | "Search my Notion for LabOS" |
| Linear | "List my assigned Linear issues" |
