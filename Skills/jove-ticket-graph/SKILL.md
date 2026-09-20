---
name: jove-ticket-graph
description: Walk a Jira ticket three hops out, read every node in full (description, comments, attachments), then do the same on Slack, and stitch one dated timeline. Use when Dhiraj is brought into a ticket, asks for the history or end action on a JVA/JPMT, or says read the chain / linked tickets / what led here.
---

# JoVE ticket graph

On-demand deep-read. Close, stay, or split is optional and comes last.

Project root is `~/dev/jove-hq`. Read [REFERENCE.md](REFERENCE.md) for prune rules, Slack hops, attachments, and JVA Closed vs Done.

Do not copy CLAUDE.md rule 14. This skill feeds it. Do not use `jove-scope-audit` for this: that walk is one hop and registry-only.

## Run

0. State the seed key. Say you are walking, not acting.
1. Print the graph before reading bodies:
   `node ~/dev/jove-hq/.claude/skills/jove-ticket-graph/scripts/walk.mjs --seed <KEY>`
   Exit 2 (no Jira token): BFS yourself with `getJiraIssue` `issuelinks` using the same FOLLOW / SKIP / mega-epic rules. Do not invent a shorter walk. `--selftest` must pass either way.
2. Every printed key, every hop: description, all comments, all attachments. Cite or abstain per file.
3. Slack hops 1 to 3 from those keys and named people. Read threads to the end. A reply outranks its parent (`jove-connectors.md`).
4. Calls and email only when a ticket or thread names them. Full transcript or full thread.
5. Write `~/dev/jove-hq/knowledge/jove-labs/STITCH-<key>-<YYYY-MM-DD>.md` with `## Sources, in order`. Classify each item: decides vs covers. Newest decision governs. An older piece still binds what it alone governs. Conflict: keep both and name the question.
6. Stop. If asked for an end action, recommend close / same ticket / follow-on from the stitch. Humanizer and egress lint only if something leaves the vault.

## Hard stops

- Depth 3 is a ceiling, not a target to exceed.
- Do not enumerate an epic's children. Record the epic as a leaf.
- Do not draft, comment, or book before the stitch exists.
- Do not Slack-draft the stitch.

## Specimen

JVA-31344: hop 2/3 held the 30-day policy (`JVA-19543`, `JVA-25045`, `JVA-25851`). The CSV was an attachment. The group DM was not on the ticket.
