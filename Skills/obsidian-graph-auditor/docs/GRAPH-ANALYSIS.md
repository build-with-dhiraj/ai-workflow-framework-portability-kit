# Graph Analysis for Obsidian Vaults

> A practitioner's guide to interpreting your audit results. Covers orphans, mega-hubs, modularity, and concrete fixes. Read this if your scorecard shows you a problem and you want to know what to do about it.

---

## Why Obsidian's built-in Graph view isn't an audit

The Graph view shows you a force-directed visualization of your vault's link structure. It's beautiful, and it's useful for staring at, and it's not a measurement. You can't tell from a hairball whether your orphan rate is 8% or 38%. You can't tell whether the giant node in the middle holds 4% of edges or 40%. You can't measure modularity by squinting.

The audit replaces visual intuition with eight numbers. This document explains how to read each one and what to do when it grades poorly.

---

## What good link density looks like

**Link density** is just edges / notes. A vault with 3,000 notes and 12,000 internal edges has a density of 4.0.

The network-science consensus for well-connected small-world graphs is 4-10. Below 1.5, you have a capture-heavy vault, you're saving notes faster than you're connecting them. Above 10, you've usually got dense bidirectional auto-linking, which is fine.

Two failure modes show up in density:

1. **Sub-2.0 density**, the "list" failure mode. The vault is a stack of captured items with weak threading between them.
2. **Sub-1.0 density**, the "archive" failure mode. The vault is functionally a backup of articles you read once, not a knowledge graph.

Concrete fix: pick the 20 lowest-degree notes and add 2-4 outgoing wikilinks each. Use frontmatter properties to make this batchable. Re-run the audit; density should jump.

---

## The orphan crisis (and the 10% threshold)

**Orphan rate** = notes with degree zero / total notes. An orphan has no incoming and no outgoing internal links.

The 10% threshold comes from Konik's PKM-as-graph framing: above 10% orphan rate, your **capture-to-connection ratio** is broken. You're shovelling content in faster than you're integrating it. Every additional orphan increases the cost of finding anything (because search ranking degrades on isolated nodes) and decreases the value of your existing graph (because the graph view becomes noisier).

Real-vault data from the development cycle that produced this tool: orphan rate dropped from **32.2% to 12.0%** in one audit-driven cleanup pass. The fix was mechanical, not creative:

1. Sort orphans by `created` date (oldest first).
2. For each orphan, do one of three things:
   - Add one outgoing wikilink to an existing related note (5 seconds).
   - Tag with a frontmatter property that participates in the graph (1 second).
   - Delete (the note was never useful, it just felt insightful in the moment).

You're not allowed to feel bad about deleting. Most captured content is read-once, and the value is in the act of reading, not the act of saving.

**A near-orphan (degree 1) is a half-orphan.** Use the same playbook. A vault with 30% near-orphans is structurally similar to a vault with 30% orphans, neither is well-connected on multiple sides.

---

## The mega-hub anti-pattern (top-hub > 5% = force-star)

**Top-hub edge-share** = weighted degree of the highest-degree note / total weighted degree.

If one note holds more than 5% of all link-weight in your vault, you have a **force-star anti-pattern**: a single super-hub with everything radiating outward and no peripheral connections. Ron Milo's network-motifs work shows force-stars have terrible retrieval properties, every query routes through the same bottleneck, and they're catastrophically fragile: lose the hub, lose the structure.

Real-vault data: the development vault had a `research` mega-hub holding **31.4%** of all edge-weight. After splitting it into ~15 topic-specific hubs, top-hub edge-share dropped to **1.14%**. The fix:

1. From the audit's "TOP HUBS" section, identify the mega-hub.
2. List its incoming wikilinks (use Obsidian's "Linked mentions" pane or `grep -rn '\[\[mega-hub\]\]'`).
3. Bucket those incoming links into 5-15 topic groups.
4. Mint a new hub note for each topic group.
5. Re-point the incoming wikilinks to the appropriate new hub.
6. Re-run the audit. Top-hub edge-share should drop dramatically.

A healthy vault has a **power-law degree distribution with a graceful tail**: the top-hub:next-hub ratio is under 2.0, meaning the second-place hub is at least half the size of the first.

---

## Louvain modularity, in plain English

**Louvain modularity** measures how cleanly your graph splits into communities. The algorithm tries to maximize within-community density while minimizing between-community density.

- Modularity below 0.3: no coherent communities. Your vault is one big hairball.
- Modularity 0.4 - 0.65: healthy. Real topics exist, bridge notes link them.
- Modularity above 0.75: siloed islands. Topics exist, but they don't connect.

The 0.40-0.65 band comes from Newman's modularity work and from Paranyushkin's InfraNodus on discourse networks. Above 0.65, you're missing bridges; below 0.40, you don't have topics yet.

**To raise low modularity:** mint topic-specific hubs (see the "mega-hub" section above), convert shared frontmatter properties to wikilinks, and tag clusters of related notes into small cliques.

**To lower high modularity:** write bridge notes that explicitly link two communities. The audit's "TOP BRIDGES" section ranks notes by betweenness centrality, these are the existing bridges in your vault. Protect them, and add more like them.

---

## How to fix each rubric dimension

| Dimension | Concrete fix | Time cost |
|---|---|---|
| Link density (low) | Sort low-degree notes; add 2-4 wikilinks each. | 10 sec / note |
| Orphan rate (high) | Sort orphans by created-date; link or delete. | 10-30 sec / orphan |
| Near-orphan rate (high) | Same as orphans; treat as "one fix away". | 5-10 sec / note |
| Connected-2plus (low) | Composite, fixed by fixing orphans + near-orphans. | derived |
| Top-hub edge-share (high) | Split mega-hub into topic-specific hubs; re-point inbound links. | 30 min one-time |
| Top-hub:next ratio (high) | Same as edge-share, or invest in second-place hub. | 30 min one-time |
| Modularity (low) | Mint hubs; convert frontmatter to wikilinks. | 1 hour |
| Modularity (high) | Write bridge notes between siloed clusters. | 1 hour / bridge |
| Frontmatter-wikilink adoption (low) | Convert top 3 frontmatter fields to `[[wikilink]]` form. Update templates. | 1 hour one-time |

The general principle: **fix the worst dimension first**. The auditor's overall grade *is* the worst dimension, by design, so the highest-leverage fix is always visible.

---

## Reading the "TOP HUBS" and "TOP BRIDGES" sections

The audit's bottom sections surface the structural notes you care most about:

**TOP HUBS (weighted degree):** the notes with the most edge-weight. The first one is your top hub. If its share is > 5%, it's a force-star, split it. If the gap between #1 and #2 is huge (ratio > 2.0), invest in #2.

**TOP BRIDGES (betweenness centrality):** the notes that sit on the shortest path between many other notes. These are the connectors that hold your communities together. **Protect them**: don't rename or merge them casually. If you delete a top bridge by accident, your modularity score will spike (artificial silos appear), and you'll lose the connecting fabric.

A healthy vault has 5-20 distinct top bridges, each in a different community. A vault where the top 10 bridges are all the same kind of note (e.g., 10 daily notes) probably has a chronological-thread anti-pattern rather than topical structure.

---

## Reading the "NOTE CLASSES" breakdown

If your vault uses the kepano convention of frontmatter `type:` values (entity / concept / theme / moc), the audit splits the orphan rate by class. This is useful: orphans among *source notes* (raw captures) are normal and expected. Orphans among *signal notes* (curated hubs and concepts) are alarming, because those notes are *meant* to be the connectors.

Example:

```
NOTE CLASSES
  signal      n=    412  orphans=     8  (1.94%)   <- healthy
  source      n=  2,715  orphans=   367  (13.52%)  <- normal, but high, review
```

The fix order is reversed by class: **fix signal-orphans first** (they're cheap and high-leverage), then turn to source-orphans.

---

## After fixing: use the baseline gate

Once you've made structural changes, re-run the audit and save the new JSON:

```bash
obsidian-graph-audit --vault ~/notes --json-out audit.json
```

From here on, every audit can compare against that baseline:

```bash
obsidian-graph-audit --vault ~/notes --baseline audit.json
```

Exit code 1 if any dimension regressed. Wire it into a pre-commit hook, a CI workflow, or a weekly cron, whichever forcing function actually fires for you.

---

## Further reading

- The full rubric with citations: [`RUBRIC.md`](RUBRIC.md).
- Tool comparison: [`COMPARISON.md`](COMPARISON.md).
- Mark Newman, [Modularity and community structure in networks](https://www.pnas.org/doi/10.1073/pnas.0601602103).
- Dmitry Paranyushkin, [InfraNodus](https://infranodus.com), discourse network analysis.
- Ron Milo et al., [Network Motifs: Simple Building Blocks of Complex Networks](https://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/network_motifs_2002_milo_science.pdf).
- Andy Matuschak, [Evergreen notes should be densely linked](https://notes.andymatuschak.org/Evergreen_notes_should_be_densely_linked).
