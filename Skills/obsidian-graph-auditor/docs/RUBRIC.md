# The 8-Dimension Grade-A Rubric for Obsidian Vaults

> This document is the authoritative reference for what the auditor measures, what counts as healthy, and why. Each dimension links to the literature that anchors its threshold.

The auditor scores eight independent dimensions of vault health. Each dimension grades A-F. The overall grade is the worst dimension, by design, so the highest-leverage fix is always visible.

A vault is **Grade A** only if every dimension is A.

---

## 1. Link density (edges per note)

**What it is.** Average number of resolved internal edges per note across the vault. A vault with 3,000 notes and 12,000 internal edges has a density of 4.0.

**Healthy range.** 4.0 - 10.0.

**Default grading.** A ≥ 4.0, B ≥ 2.5, C ≥ 1.5, D ≥ 0.8, F < 0.8.

**Why.** Andy Matuschak's evergreen-notes practice describes well-connected notes as "well-connected on multiple sides", empirically, the small-world graphs that retrieve well sit around 4-10 average degree. Below 1.5 you have a capture-heavy vault that isn't connecting; the graph is closer to a list than a network. Above 10 typically means dense bidirectional auto-linking and is usually fine.

**How to fix it.** Pick a low-degree note and add 2-4 wikilinks to existing notes that share concepts. Use frontmatter properties (kepano "Properties as links") to convert metadata into edges automatically.

**Sources.**
- Andy Matuschak, [evergreen notes](https://notes.andymatuschak.org/Evergreen_notes_should_be_densely_linked).
- kepano, [Properties as links](https://stephanango.com/properties-as-links).
- Network-science textbooks (Newman, Barabási) on small-world parameters.

---

## 2. Orphan rate (degree 0)

**What it is.** Percentage of notes with zero internal edges. A note that nothing links to and that links to nothing is an orphan.

**Healthy range.** < 10%.

**Default grading.** A ≤ 10%, B ≤ 20%, C ≤ 30%, D ≤ 40%, F > 40%.

**Why.** Konik's PKM-as-graph framing treats orphan rate as a **capture-to-connection ratio**: above 10% means you're collecting faster than you're integrating, and the asymmetry compounds. Ann P.'s "Your Second Brain Is Broken" argues the same point from a retrieval angle: orphans are the dead-weight that makes your vault a "write-only archive".

**How to fix it.** Sort notes by `created` date, walk the oldest orphans first, and either (a) add an outgoing wikilink to an existing note, (b) tag with frontmatter properties that already participate in the graph, or (c) delete. The audit-driven cleanup that produced the README's before/after table moved orphan rate from 32.2% to 12.0% in one pass.

**Sources.**
- Sebastian Konik, PKM-as-graph essays.
- Ann P., ["Your Second Brain Is Broken"](https://medium.com/@ann_p/your-second-brain-is-broken-why-most-pkm-tools-waste-your-time-76e41dfc6747).
- Obsidian Forum [Find orphan notes](https://forum.obsidian.md/t/find-orphan-notes/817), the most active community thread on this exact pain.

---

## 3. Near-orphan rate (degree 1)

**What it is.** Percentage of notes with exactly one internal edge. Near-orphans are dangling tendrils, connected but not integrated.

**Healthy range.** < 15%.

**Default grading.** A ≤ 15%, B ≤ 25%, C ≤ 35%, D ≤ 45%, F > 45%.

**Why.** Near-orphans are the natural derived complement of the orphan threshold: if your orphan rate is under 10%, your single-edge rate should be under 15%, because Matuschak's "well-connected on multiple sides" rule fails at degree 1 as much as it fails at degree 0. Empirically, the difference between a vault that retrieves well and one that doesn't isn't the deg-0 number; it's the deg-1 number.

**How to fix it.** Same playbook as orphans. Bonus: deg-1 notes are higher-leverage than deg-0 because you've already paid the capture cost, adding a second edge is a one-line fix.

---

## 4. Connected ≥2 share

**What it is.** Percentage of notes with two or more internal edges. The complement of (orphans + near-orphans).

**Healthy range.** > 75%.

**Default grading.** A ≥ 75%, B ≥ 60%, C ≥ 45%, D ≥ 30%, F < 30%.

**Why.** This is the affirmative form of the orphan + near-orphan thresholds. A healthy vault has at least three-quarters of its notes participating in the graph at degree 2 or higher.

---

## 5. Top-hub edge-share

**What it is.** Percentage of total weighted edges concentrated on the single highest-degree note. If one tag captures 30% of all link-weight in the vault, top-hub edge-share is 30%.

**Healthy range.** < 5%.

**Default grading.** A ≤ 5%, B ≤ 10%, C ≤ 15%, D ≤ 20%, F > 20%.

**Why.** Network-science calls this a "force-star" anti-pattern: one super-hub with everything radiating outward and nothing connecting peripherally. Ron Milo's work on network motifs shows that force-stars have terrible retrieval properties, every query routes through the same bottleneck. Above 5%, your vault is one tag's worth of damage from collapse.

**How to fix it.** Identify the mega-hub from the auditor's "TOP HUBS" section, then split it into 5-15 topic-specific hubs and redirect inbound links. The audit on the development vault dropped top-hub edge-share from 31.4% to 1.14% with this single fix.

**Sources.**
- Ron Milo et al., [network motifs / force-star anti-pattern](https://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/network_motifs_2002_milo_science.pdf).
- Barabási, scale-free networks and concentration tradeoffs.

---

## 6. Top-hub : next-hub ratio

**What it is.** Weighted degree of the top hub divided by the weighted degree of the second-most-connected note.

**Healthy range.** < 2.0.

**Default grading.** A ≤ 2.0, B ≤ 3.0, C ≤ 5.0, D ≤ 8.0, F > 8.0.

**Why.** A healthy power-law tail has the second-place hub at half the first-place hub or above (ratio < 2.0). When the ratio is 8+, you have a single dominant hub with no second tier, which means there's no graceful failover when that hub gets split, renamed, or refactored.

**How to fix it.** Same as top-hub edge-share: split the dominant hub, or invest in the second-tier hubs by adding edges to them.

---

## 7. Louvain modularity

**What it is.** A measure of how well the graph splits into communities. Computed by the Louvain algorithm on the weighted graph. Range: roughly 0.0 to 1.0.

**Healthy range.** 0.40 - 0.65.

**Default grading.** A in [0.40, 0.65]; B in [0.30, 0.75]; C in [0.20, 0.85]; D below 0.10; F outside all.

**Why.** Newman's modularity work and Dmitry Paranyushkin's InfraNodus give the canonical band: below 0.4 your vault has no coherent communities (one big hairball); above 0.65 your communities are siloed islands with no inter-cluster bridges. The 0.40-0.65 band is where a vault has real topics that *also* connect through bridge notes.

**How to fix it (low modularity).** Mint topic-specific hubs. Connect notes that share a tag into a small clique. Convert one shared frontmatter property into a wikilink.

**How to fix it (high modularity).** Write bridge notes that explicitly link two communities. The auditor's "TOP BRIDGES" section by betweenness centrality identifies your current bridges; protect them and add more.

**Sources.**
- Mark Newman, [Modularity and community structure in networks](https://www.pnas.org/doi/10.1073/pnas.0601602103).
- Dmitry Paranyushkin, [InfraNodus discourse network analysis](https://infranodus.com).
- Blondel et al., [Louvain algorithm](https://en.wikipedia.org/wiki/Louvain_method).

---

## 8. Frontmatter-wikilink adoption

**What it is.** Percentage of notes with at least one `[[wikilink]]` somewhere in their YAML frontmatter. Captures kepano-style typed metadata.

**Healthy range.** > 80%.

**Default grading.** A ≥ 80%, B ≥ 60%, C ≥ 40%, D ≥ 20%, F < 20%.

**Why.** kepano's "Properties as links" convention converts metadata into graph edges, `author: [[Jane Doe]]`, `source: [[Conference 2026]]`, `topic: [[Graph Theory]]`. When adoption is high, the graph has structured, typed edges, not just unstructured body wikilinks. This makes the auditor's other metrics dramatically more reliable.

**How to fix it.** Pick the three frontmatter fields you use most often (`source`, `author`, `topic`) and convert them to wikilink form. Add them to your template. The audit on the development vault moved adoption from 6% to 84% by adding a single resolver pass.

**Sources.**
- kepano, [Properties as links](https://stephanango.com/properties-as-links).
- kepano, [obsidian-skills](https://github.com/kepano/obsidian-skills).

---

## Customizing the thresholds

The defaults represent one defensible reading of the literature. Reasonable people use different ones, a zettelkasten purist might want a stricter `orphan_pct`, a digital-garden author might want a looser `top_hub_edge_share_pct`.

Pass any subset to the CLI:

```bash
obsidian-graph-audit --vault ~/notes --threshold-config my-rubric.yaml
```

```yaml
# my-rubric.yaml, override just the dimensions you disagree with
orphan_pct:
  a: 15.0
  b: 25.0
  c: 35.0
  d: 45.0
top_hub_edge_share_pct:
  a: 8.0
  b: 15.0
  c: 25.0
  d: 35.0
```

Unspecified dimensions fall back to the defaults in this document.

---

## Why no recall / precision / "personal usefulness" dimensions?

Recall and personal-usefulness metrics require ground-truth labels or longitudinal user data the auditor doesn't have. The eight dimensions in this rubric are all **purely structural**, they can be computed deterministically from the vault's link graph alone, with no LLM in the loop. That's the gate the auditor passes; subjective dimensions are out of scope on purpose.

---

## References

1. Andy Matuschak, [Evergreen notes should be densely linked](https://notes.andymatuschak.org/Evergreen_notes_should_be_densely_linked).
2. Sönke Ahrens, *How to Take Smart Notes* (2017).
3. kepano (Steph Ango), [Properties as links](https://stephanango.com/properties-as-links) and [obsidian-skills](https://github.com/kepano/obsidian-skills).
4. Sebastian Konik, PKM-as-graph series.
5. Dmitry Paranyushkin, [InfraNodus](https://infranodus.com) and discourse network analysis.
6. Mark Newman, [Modularity and community structure in networks](https://www.pnas.org/doi/10.1073/pnas.0601602103).
7. Ron Milo et al., [Network Motifs: Simple Building Blocks of Complex Networks](https://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/network_motifs_2002_milo_science.pdf).
8. Blondel et al., [Fast unfolding of communities in large networks (Louvain)](https://iopscience.iop.org/article/10.1088/1742-5468/2008/10/P10008).
