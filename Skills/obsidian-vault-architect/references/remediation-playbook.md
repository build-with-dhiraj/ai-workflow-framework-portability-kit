# The Remediation Lever Stack

An ordered playbook for driving a vault toward Grade-A without losing a note or degrading retrieval. Sequencing matters: each lever unlocks the next. Generalize the worker names below to whatever tools you have (an NER extractor, an entity-resolver, a community detector, a vector indexer); the companion skills `obsidian-orphan-killer`, `obsidian-graph-auditor`, and `obsidian-brain-eval` implement much of this.

## Engineering discipline (applies to every lever)
- **Back up first.** Branch + commit, or a filesystem snapshot. Vault content is often gitignored for privacy, so git alone may not protect it.
- **Dry-run + cost-forecast before any mutating or LLM step.** Sample, forecast token cost from the real gap, then write once. No narrow-then-wide re-runs.
- **Additive and idempotent.** Stamp what you touch (`*_enriched_at`, `resolved_at`, `provenance`) so you can skip already-done work and revert.
- **Frontmatter-only vs body-changing.** Resolving/anchoring/tagging edits frontmatter only, which must NOT change the body content-hash, so the vector index does not re-embed. Only genuinely body-changing steps (stub expansion, digest creation) trigger re-embedding.
- **Never delete.** Orphan fixes append; thin-note expansion preserves the original body under a flagged section.
- **Measure before and after every lever** with the auditor's JSON output, so each lever's delta is attributable.
- **For long ingest/distill/index jobs**, use the resumable + idempotent + detached pipeline patterns in `scale-and-anti-patterns.md` (scope-keyed sidecar state, body-only content-hash change detection, dry-run cost gate) so a multi-hour remediation survives kills, sleeps, and reruns with zero re-spend.

## Phase 1 — Metadata enrichment (create link targets)
1. **Re-extract entities on the gaps.** Re-run NER on notes that were never extracted or whose extraction truncated (raise the model's max-tokens / max-body limits for recovery). Output goes into the `entities`/`topics` frontmatter.
2. **Backfill the alias table.** Generate surface-form → canonical-hub aliases so the resolver can place links. Gate generated aliases through a guard gauntlet (not a substring, no cross-domain collision, sanity-checked, confirmed) to avoid bad merges. Dry-run first.
3. **Grounded stub expansion (thin notes only).** For genuinely thin notes, retrieve the note's own neighbors + top-k vector neighbors and write a short context paragraph that **cites only those sources**, appended under a flagged `## Context (synthesized)` section with `provenance`. Never free-form; skip if no grounded source exists. Re-extract entities on expanded notes. This is a body-changing step, so re-embed afterward.

## Phase 2 — Deterministic resolve + anchor + mint (cheap, no LLM at the core)
4. **Re-resolve everything** with the expanded alias table. Rewrite a mention to `[[Hub]]` **only when the hub file exists** (never create dangling links). This is the single biggest lever for orphans, near-orphans, density, and connectivity.
5. **Anchor remaining true orphans.** For orphans with no resolvable entity, attach a `related:` link to the most semantically similar existing concept hub (cosine threshold, capped per hub, reviewed). Frontmatter-only.
6. **Cluster-mint orphan clusters.** Embed the leftover orphans, cluster them, name each cluster, and mint a new concept hub per cluster. These new hubs double as bridges. Review the minted names before committing.

## Phase 3 — Densify stars + bridge communities
7. **Digest/anchor the import-stars.** For each large single-source batch (e.g., transcripts from one channel), cluster by embedding, write a map-reduce TL;DR per cluster, and create a **digest anchor note** that links the batch members to the relevant *topic* hubs. This densifies the star and pulls it into real communities (every haystack-only batch still earns aggregate graph anchors, so a graph-reading pattern-finder can see what otherwise lives only in the archive: the dual-layer rule, decision 8 in SKILL.md).
8. **Mint community-bridge MOCs.** From the community + top-hub list, connect obviously-related community hubs (e.g., `[[Open Access]]` ↔ `[[Peer Review]]` ↔ `[[Preprints]]`) with small `type: moc` bridge notes carrying reciprocal `related:` links. **Cross-community edges are the only lever that lowers modularity** out of the over-siloed band.

## Phase 4 — Density top-up (only if density is still < 4.0)
9. **Deterministic overlap linking.** Jaccard entity-overlap between notes, no LLM. Add a link when overlap clears a threshold.
10. **Vector top-k related linking.** Cosine top-k neighbors, quality-capped. **Stop the moment density hits 4.0 or links start getting weak** — do not manufacture junk edges to chase a number.

## Phase 5 — Recompute, re-index, measure, gate
11. **Recompute communities + tags** (Louvain, fixed seed) and re-stamp community tags.
12. **Re-index only body-changed notes** (stub-expanded + digest notes). Frontmatter-only changes must not re-embed.
13. **Re-audit all 8 dimensions** and compare to baseline.
14. **Recall@K gate.** Generate (or refresh) a gold question set, score Recall@10 (target ≥ 0.85) overall **and** on the formerly-orphaned subset (proves de-orphaned notes are now retrievable). If Recall drops, halt and fix retrieval before continuing.

## Phase 6 — Iterate to A (or an honest near-A)
- Density < 4.0 → more genuine links (Phase 4).
- Orphan / near-orphan high → more enrich / anchor / mint (Phases 1–2).
- Modularity > 0.65 → more bridge MOCs (Phase 3).
- **Stop at genuine A, or at an honest near-A when the only path to A is junk links that would drop Recall.** Document which, and why.
