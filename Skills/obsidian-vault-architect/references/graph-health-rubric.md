# The 8-Dimension Graph-Health Rubric

A vault's health is not "how many notes" but "how well-connected, how balanced, and how retrievable." These eight dimensions measure that. They are grounded in network science (small-world graphs, power-law degree distributions, Louvain community detection) and PKM practice.

> These are the design **targets** an architect builds toward. `obsidian-graph-auditor` measures them; the frontmatter-wikilink schema in `note-model-and-schema.md` enables them; the levers in `remediation-playbook.md` are how you reach them. Route archive-shaped content out of the graph entirely per the dual-layer rule (decision 8 in SKILL.md; companion `memory-router`) so the rubric judges signal, not haystack.

## Grading philosophy: worst-of-8
The vault's overall grade is the **minimum** grade across all eight dimensions. One F drags the whole vault to F. This is deliberate: it always surfaces your single highest-leverage fix. Do not average; chase the worst dimension.

## The eight dimensions

| # | Dimension | What it measures | A-grade threshold | Failure signature | Why it matters |
|---|---|---|---|---|---|
| 1 | **Link density** | Avg edges per note (total edges ÷ total notes) | **≥ 4.0** | < 1.5 = capture-heavy, not connecting | Connectivity saturation; a well-linked note is a discoverable note |
| 2 | **Orphan %** | Notes with degree 0 | **≤ 10%** | > 30% = capture is not reaching the graph | A note with zero links is invisible to thought and to retrieval |
| 3 | **Near-orphan %** | Notes with degree exactly 1 | **≤ 15%** | > 25% = fragile leaves hanging off one node | One link is brittle; lose it and the note re-orphans |
| 4 | **Connected ≥2 %** | Notes with degree ≥ 2 | **≥ 75%** | < 45% = most notes aren't truly integrated | The positive inverse: most notes should sit in a web, not a thread |
| 5 | **Top-hub edge-share** | % of all edges that touch the single most-connected node | **≤ 5%** | > 15% = one mega-hub dominates (a star graph) | Avoids a power-law pathology where one node is a bottleneck |
| 6 | **Top:next hub ratio** | Edges on hub #1 ÷ edges on hub #2 | **≤ 2.0** | > 3 = a cliff between the top two hubs | A healthy degree distribution declines gently, it does not spike |
| 7 | **Modularity** | Louvain community-clustering score (−1..1) | **0.40 – 0.65** | < 0.4 = amorphous blob; > 0.65 = siloed islands | Communities should be real but talk to each other |
| 8 | **Frontmatter-wikilink adoption** | % of notes with ≥1 `[[wikilink]]` in a YAML property | **≥ 80%** | < 40% = links live only in body text | Typed metadata (entities/topics/related) drives queries and reranking |

### Measurement definitions (be precise)
- **Link density** = total directed edges ÷ total notes.
- **Orphan / near-orphan / connected** are partitions of all notes by degree (0 / exactly 1 / ≥2). They sum to 100%.
- **Top-hub edge-share** = edges incident to the #1 node ÷ total edges.
- **Top:next ratio** = degree(hub #1) ÷ degree(hub #2). If only one hub exists, grade A by default.
- **Modularity** = Louvain (use a fixed seed, weighted edges, no resolution tuning) so the score is reproducible. Lower modularity by *adding cross-community edges*, never by tuning the algorithm.
- **Frontmatter-wikilink adoption** = notes with ≥1 wikilink in any YAML field (`entities`, `topics`, `related`, …) ÷ total notes.

### Full grading bands (from the companion auditor)
The auditor grades each dimension A/B/C/D/F. Indicative band edges:
- Link density: A ≥4.0, B ≥2.5, C ≥1.5, D ≥0.8.
- Orphan %: A ≤10, B ≤20, C ≤30, D ≤40.
- Near-orphan %: A ≤15, B ≤25, C ≤35, D ≤45.
- Connected ≥2 %: A ≥75, B ≥60, C ≥45, D ≥30.
- Top-hub edge-share: A ≤5, B ≤10, C ≤15, D ≤20.
- Top:next ratio: A ≤2, B ≤3, C ≤5, D ≤8.
- Modularity: A 0.40–0.65, B 0.30–0.75, C 0.20–0.85, else D/F.
- Frontmatter-wikilink adoption: A ≥80, B ≥60, C ≥40, D ≥20.

---

## The diagnostic root-cause model

Almost every failing vault fails for one (or a mix) of three reasons. Read the rubric to tell which.

### 1. Under-linked periphery (orphans + near-orphans high; density + connected low)
A large outer ring of notes with 0 or 1 link. Usually a *metadata* problem, not a content problem:
- The note was **never entity-extracted** (no NER run, body too short, extraction truncated).
- The note **has entities but they were never resolved to links** (alias misses, the target hub doesn't exist yet).
- The note is **genuinely thin** (<~200 chars) and low-value.
Tell these apart before fixing: count how many orphans already carry `entities`/`topics` (a cheap deterministic fix) vs how many were never extracted vs how many are truly thin (these may legitimately stay as archive leaves).

### 2. Over-siloed communities (modularity too high, e.g. > 0.7)
Many distinct clusters, but few edges cross a community boundary. Obviously-related domains sit as separate islands. The fix is **cross-community bridges**, not more within-community links.
- Caveat: a genuinely multi-domain vault (several unrelated life/work domains) will naturally sit a bit high (~0.75). The A-band assumes a more coherent single domain. **An honest 0.75 with real structure beats a forced 0.65 built from junk links.**

### 3. Hub concentration / "stars" (top-hub edge-share + top:next ratio too high)
One node hoards the edges, or a batch of imported items (e.g., transcripts from a single source) all link to one topic hub and to nothing else, forming a dense "star." The graph looks like a few spheres connected by thin threads.
- Fix mega-hubs by **splitting** them into sub-hubs and re-pointing edges.
- Fix import-stars with **digest/anchor notes** that link the batch members to multiple relevant hubs (see the remediation playbook).

### Reading modularity
- **< 0.40** — no coherent communities; everything links to everything (rare in real PKM).
- **0.40 – 0.65** — healthy: real clusters that still cross-pollinate.
- **> 0.65** — siloed; communities barely talk. Add bridges.

Use the rubric as a *targeting system*: the worst dimension names the root cause, the root cause names the lever.
