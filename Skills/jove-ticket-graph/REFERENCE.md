# jove-ticket-graph reference

## Jira walk

`walk.mjs` BFS `issuelinks` to depth 3.

**FOLLOW** (any direction): Relates, Blocks, Duplicate, Clones, Action item, Escalate, Resolve, Problem/Incident, Work item split, Parent-Child when the parent is not a mega-epic, JPMT↔JVA in either direction.

**SKIP** (do not enqueue): any Gantt link, any Polar / Polaris link, Tested By.

**Mega-epic leaf.** If the node is an Epic, or its Epic Link / parent is `JVA-29512` (JoVE Labs V2) or any other epic whose children are the board: include that epic key as a leaf at this hop (key, summary, status). Do not follow its links. Do not list siblings. Follow a child only when a comment or Slack message already on this chain names that child.

Moved keys redirect. Compare the returned key to the queried key. Cite the live key.

## What "read in full" means

For each graph node:

- description
- every comment, oldest first
- every attachment: CSV, PDF, PNG, email, query dump, sheet export. Download and read. A filename in the comment list is not a read.
- status, assignee, reporter, created, updated, link type that brought you here

JPMT is the requirement. JVA is the work. Purpose questions go to the original reporter in Jira comments (CLAUDE.md rule 15).

## Slack hops (same ceiling)

**Hop 1.** Search the seed key (and the JPMT if the seed is a JVA) across public and private. Read every matching thread to the end. Include channels and DMs the ticket already names.

**Hop 2.** From those threads: other JVA/JPMT keys, other channels, named people. Search and read those threads.

**Hop 3.** One more expansion. Then stop.

`slack_read_channel` is parents only. Unopened threads are unread. See `jove-connectors.md`.

## Calls and email

Enter the graph only when a ticket or Slack thread names them. Then full transcript or full thread. Highlights are not a read.

## Stitch file

Path: `knowledge/jove-labs/STITCH-<seed>-<YYYY-MM-DD>.md`

```yaml
---
moc: "[[jove-labs]]"
type: stitch
seed: JVA-00000
date: YYYY-MM-DD
owner: Dhiraj Pawar
status: stitched
---
```

Required heading: `## Sources, in order`. Each line: absolute timestamp, surface, permalink or key, one clause (decides / covers). Copy that section into any later `ticket-draft` or `outbox` so `provenance-check.mjs` can gate it.

## End action (only if asked)

Read JVA status names as Jira means them, not as English:

- **Closed**: no code change
- **Done**: code shipped

Do not reopen a Done sibling to add scope. Relates-to for context. Reporter cannot be set on JVA create; name the purpose owner in the description.

Notify on the ticket you were brought into, ADF mentions. Slack MCP cannot delete drafts.

Calendar: propose slots unless Dhiraj says book. Book = freebusy, one mutual slot, `sendUpdates=all`.
