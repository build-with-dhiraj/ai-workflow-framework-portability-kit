# Scale Ceilings, Anti-Patterns & Pipeline Patterns

Vaults don't die from missing features — they die from **fragmentation, graph bloat, and non-resumable jobs**. This file is the pre-mortem: the ceilings you'll hit, the anti-patterns that caused real bugs, and the engineering patterns that make a knowledge pipeline survivable.

## Scale ceilings (design for these from day one)

| Ceiling | Where it bites | The fix |
|---|---|---|
| **Global graph view collapses ~10–25K notes** | The pretty force-graph becomes an unreadable hairball and lags the app | Don't rely on the global graph for navigation. Use the **local graph** (depth 1–2) + theme MOCs + `_index.md`. The graph is a toy past mid-size. |
| **Vector index fragmentation** | Per-row upserts create many small fragments → ANN latency climbs, recall drops | **Batch upsert + `optimize()`/compact** when fragments approach ~50. Never `merge_insert` one row at a time in a loop. |
| **Dataview re-runs every query on every render** | Many live Dataview blocks → editor lag at scale | Prefer **Bases** (native, indexed, faster) for dashboards; reserve Dataview for one-off ad-hoc queries. |
| **Deep folder taxonomies** | Re-filing and re-linking becomes O(everything); notes get stranded | Shallow folders for *lifecycle only*; topic via `themes` + MOCs (many-to-many). |
| **Re-embedding the whole corpus on every run** | Cost + time balloon as the vault grows | **Incremental indexing** keyed on a **body-only content hash**; touch only changed notes. |
| **One index per scope** | Infra sprawl; cross-scope queries become joins | **One shared table, a `scope` field, `WHERE` prefilter.** |

## Anti-patterns (each one bit us for real)

1. **Hardcoded template values masquerading as data.** A note's byline/attribution/scope rendered from a constant in the note-writing template instead of from the note's own frontmatter. Symptom: every note in scope B is stamped with scope A's name. *Fix:* templates derive every displayed field from the note's frontmatter (`mentor`/`author`/etc.); add a lint that flags a byline that disagrees with frontmatter. **The primary fix is always the template, not a mass-rewrite of existing notes** — only batch-correct already-written notes when it's trivially scriptable and explicitly wanted.

2. **Pipeline state stored in note frontmatter.** `indexed: true`, `last_run: <timestamp>`, processing flags living in the note. Symptoms: a stamp flips the file hash → needless re-embed; the graph/Bases fill with machine noise. *Fix:* pipeline state goes in a **sidecar** (`_system/<stage>_done.json`, scope-keyed), never in the note. Notes hold knowledge; sidecars hold bookkeeping.

3. **Per-row vector upserts.** The fragmentation killer above. *Fix:* batch + optimize.

4. **Mutating raw sources.** Editing a transcript/essay after capture breaks every citation anchored to it. *Fix:* `raw/` is append-only/immutable; corrections live as atomic notes that supersede.

5. **Fat notes as the retrieval unit.** "Everything about X" notes retrieve as mush and bury the specific claim. *Fix:* atomic notes — one idea each.

6. **Averaging away contradictions.** When two sources disagree, a naive merge blends them into a bland mean that's true to neither. *Fix:* preserve both, label the tension (esp. for persona/voice vaults — see cartography-and-personas).

7. **Themes as free-text tags, not linkable entities.** `themes: [some-free-text]` that never becomes a note → no MOC, no graph cross-linking, dead-end classification. *Fix:* themes are wikilink-able and get MOCs via cartography.

8. **Non-resumable long jobs.** A 6-hour ingest/distill that loses everything on a kill, a laptop sleep, or a 429 storm. *Fix:* the pipeline patterns below.

9. **Cross-scope retrieval bleed.** Forgetting the scope prefilter → scope A's notes answer a scope-B query. *Fix:* `WHERE scope = '...'` prefilter, and a test that a scope-A query returns zero scope-B rows.

10. **Stale shared cache reused across scopes.** A merge/dedup cache keyed by working-dir, not scope, gets reused for the next scope → instant garbage ("0 merged"). *Fix:* key every cache by scope, or clear it and run fresh when scope changes.

## Pipeline patterns (make ingestion survivable)

For any non-trivial ingest → distill → merge → index pipeline:

- **Resumable + idempotent.** Every stage records done-units in a scope-keyed sidecar (`_system/<stage>_done.json`) and is disk-first: re-running skips completed units by checking the sidecar *and* what's already on disk. A rerun after any failure costs zero re-spend.
- **Detached for long runs.** Run multi-hour stages as detached/background processes so a dropped session or closed laptop doesn't kill them; supervise by polling the sidecar/disk, not by holding the process open.
- **Scope-keyed state, never global.** `done.json` is keyed by scope so parallel scopes don't collide.
- **Parallel via isolation.** To run multiple scopes at once, isolate each (e.g. a **git worktree** per scope) so their working state and any per-dir caches don't stomp each other. Serialize only the **shared-index write** (one scope into the shared table at a time); everything upstream parallelizes.
- **Content-hash change detection** (body-only) so reruns re-embed only what truly changed.
- **Cost logging + a dry-run gate.** Before a paid pass (transcription, LLM distill), forecast cost on a free enumeration and gate on it. Log cumulative spend.
- **Quotas are a first-class failure.** External APIs (transcription, embeddings) hit hard limits. Detect, pause gracefully, hold the affected scope, and surface it — don't crash the whole run.
