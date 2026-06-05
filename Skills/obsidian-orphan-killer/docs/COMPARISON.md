# How obsidian-orphan-killer compares

The Obsidian / PKM ecosystem has several tools that touch orphans. **None of them auto-fix orphans.** That's the wedge.

This page is the long-form version of the README's comparison table.

---

## Feature matrix

| Feature | obsidian-orphan-killer | Find Unlinked Files (Vinzent03) | Various Complements | Janitor | Dangling Links (Curtis McHale) | Smart Connections (Brian Petro) | obsidian-graph-auditor |
|---|---|---|---|---|---|---|---|
| **Lists orphans** | yes | yes | yes | yes | yes | partial | yes |
| **Auto-fixes orphans** | **yes** | no | no | no | no | no | no |
| **Resolves plain-string entities to wikilinks** | **yes** | no | partial (autocomplete UI) | no | no | no | no |
| **Embedding-based hub matching** | **yes** | no | no | no | no | yes (chat-focused, not auto-link) | no |
| **Cluster + mint new hubs** | **yes (experimental)** | no | no | no | no | no | no |
| **Frontmatter-only safety guarantee** | **yes** | n/a (read-only) | yes (autocomplete only) | yes | yes (link surface) | partial | yes (read-only) |
| **Atomic writes** | yes | n/a | n/a | n/a | n/a | n/a | n/a |
| **Idempotency stamps** | yes | n/a | n/a | n/a | n/a | n/a | n/a |
| **Dangling-link guard** | yes | n/a | n/a | n/a | n/a | n/a | n/a |
| **Per-hub absorption cap (anti-star)** | yes | n/a | n/a | n/a | n/a | n/a | n/a |
| **DO_NOT_MERGE pairs** | yes | n/a | n/a | n/a | n/a | n/a | n/a |
| **CLI / scriptable** | **yes** | no (plugin) | no (plugin) | no (plugin) | no (plugin) | no (plugin) | yes |
| **Cross-CLI skill compat (Claude Code / Cursor / Gemini / Codex)** | **yes** | no | no | no | no | no | yes |
| **Audit TSV / dry-run** | **yes (per-mode)** | partial (preview) | n/a | partial | partial | n/a | yes |
| **No GPT required (default)** | yes (resolve + anchor) | yes | yes | yes | yes | no | yes |
| **Local embeddings ($0)** | yes (fastembed) | n/a | n/a | n/a | n/a | partial | n/a |
| **Pluggable LLM** | yes (mint mode) | n/a | n/a | n/a | n/a | partial | n/a |
| **Vault-tool-agnostic (Logseq / Foam / Quartz)** | yes | partial | no | no | no | no | yes |
| **MIT licensed** | yes | varies | yes | yes | yes | partial | yes |

---

## Detailed comparisons

### vs Find Unlinked Files (Vinzent03)

The reference orphan-finder. Surfaces every note with no inbound link. **Critically: it does not fix anything.** The user is expected to manually wikilink each surfaced note. For a vault with 200 orphans, that's a multi-hour manual project; for a vault with 2,000 orphans, it's unfeasible.

orphan-killer auto-resolves the deterministic cases (alias-table → existing hubs) and embedding-anchors the rest. The output of Find Unlinked Files is the INPUT to orphan-killer's job.

### vs Various Complements

Provides autocomplete-as-you-type for wikilinks. Useful for *new* notes but does not back-fill old orphans. Different problem, different tool.

### vs Janitor

Surfaces a maintenance dashboard (broken links, large files, orphans). Like Find Unlinked Files: surfaces, doesn't fix.

### vs Dangling Links (Curtis McHale)

Specifically surfaces dangling (`[[non-existent]]`) wikilinks. The orphan-killer's **dangling-link guard** prevents these from being introduced in the first place. The two tools are complementary: Dangling Links catches old dangling links the user introduced manually; orphan-killer makes sure auto-resolution never creates new ones.

### vs Smart Connections (Brian Petro)

Excellent local-embedding chat over the vault. Surfaces similar notes in a sidebar. **Does not auto-link.** Smart Connections is read-side (retrieve relevant notes when you query); orphan-killer is write-side (modify the graph structure).

The two tools are highly complementary. After running orphan-killer, Smart Connections has a much denser graph to retrieve over.

### vs obsidian-graph-auditor

Read-only diagnostic on the 8-dimension Grade-A rubric. **Audits, doesn't treat.** It tells you your vault has 32% orphans and a force-star hub absorbing 31% of edges. The orphan-killer drops orphans to <10% and breaks the force-star by attaching orphans to their correct (non-force-star) hubs.

These two tools are **the recommended workflow**:

```bash
# 1. Audit (read-only).
obsidian-graph-audit --vault ~/vault

# 2. Resolve (no network, $0).
obsidian-orphan-killer resolve --vault ~/vault

# 3. Anchor (local embeddings, $0).
obsidian-orphan-killer anchor --vault ~/vault

# 4. Re-audit.
obsidian-graph-audit --vault ~/vault --baseline pre-audit.json
```

Step 4 should show every dimension improving. If it doesn't, file an issue.

---

## Why these guards matter (the failure modes)

Every guard on the safety contract came from a specific failure mode observed on a real 3,000-note vault:

| Failure mode | Without guard | With guard |
|---|---|---|
| **Body re-embed explosion** | Mutating any byte of the note body invalidates the LanceDB content hash, triggering a 7.5GB re-embed of the entire vault. | Body-only hash preserved → no re-embed. |
| **Force-star formation** | The LanceDB nearest-neighbor for orphans tends to be a single "research" hub, which absorbs all 800 orphans in one run and becomes a 31%-edge-share mega-hub. | Per-hub absorption cap caps any single hub at 50 orphans per run. |
| **Brand leak** | "spreadsheet formulas tutorial" anchors to `[[microsoft-excel]]` (a product hub) because the embedding model knows the topical association. | Concepts-only by default; entity hubs excluded from the candidate set. |
| **Dangling links** | The alias table claims a hub but the file was deleted; the rewriter writes `[[deleted-hub]]` and now the graph view shows a phantom node. | Dangling-link guard checks `slug in hub_slugs` at write time, not at table-build time. |
| **DO_NOT_MERGE false collapse** | `Claude AI` and `Claude Code` have cosine 0.91; the embedding leg collapses them. | User-supplied DO_NOT_MERGE list blocks them before any rewrite. |
| **Junk hub minting** | The LLM proposes `Science` as a cluster name. A hub called Science would absorb half the vault. | TOPIC_DENYLIST + CLUSTER_GENERIC_DENY reject it; cluster's orphans stay as haystack. |

None of these are theoretical. All were observed before the guards were added.

---

## Open questions / future work

- Should `resolve` mode support a `--embed-residuals` leg that hands unresolved residuals to an embedding+LLM identity confirm? The prototype supports it; the open-source v0.1 does not.
- Should `anchor` mode support typed `relationships:` outputs (e.g. `uses [[X]]`) instead of generic `entities`? Probably yes, in v0.2.
- Should there be a `de-star` mode that retroactively strips redundant `[[force-star-hub]]` links from notes already anchored to a more specific hub? Deferred to v0.2 (it's Connecting-Dots-specific in the prototype).

PRs welcome.
