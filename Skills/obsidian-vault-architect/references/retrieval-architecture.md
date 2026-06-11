# Retrieval Architecture: Plugins vs External Vector RAG

The single highest-leverage decision when the vault must be **queryable by an LLM**. The locked default: **external vector RAG**, not in-Obsidian AI plugins. Here's the decision and how to build it.

## The decision (and why plugins lose for serious retrieval)

| Requirement | Obsidian AI plugins (Copilot, Smart Connections, etc.) | External vector RAG (own pipeline) |
|---|---|---|
| **Deterministic citations** | Weak — answers drift from sources; block-level provenance is inconsistent | Strong — you attach `source + anchor` *before* the LLM runs; it cannot un-cite |
| **Hard scoping / isolation** | Limited — folder/tag filters are coarse; cross-scope bleed is common | Exact — `WHERE scope = '...'` prefilter guarantees no bleed |
| **Persona / voice control** | None — generic RAG answer | Full — you own the system prompt, guardrails, persona card |
| **Embedding/model choice** | Locked to plugin's defaults | Yours — local `bge-small`/`fastembed`, any LLM, any provider |
| **Hybrid (FTS + vector)** | Varies, often vector-only | Yours to tune (BM25 + ANN + rerank) |
| **Durability / lock-in** | Tied to a plugin's lifecycle & format | Plain markdown in, external index out — vault stays portable |
| **Cost control** | Opaque | Explicit; batch + local embeddings = near-zero |

**Verdict:** Use plugins for *in-app convenience search* if you like, but the **system of record for LLM querying is an external vector store you control.** The vault stays pure markdown (file-over-app); retrieval is a derived, rebuildable artifact.

When plugins *are* fine: a small personal vault, casual semantic search, no citation/scoping/persona requirements. Don't over-build for that.

## Reference architecture

```
vault (markdown, source of truth)
   │  walk atomic/ (+ raw/ for anchors), read frontmatter
   ▼
embed  (local: fastembed / bge-small)  ──►  vector store (LanceDB / pinecone / etc.)
   │                                          row = {id, vector, text, scope, note_type, kind, source_ref, body_hash}
   ▼
query  →  hybrid search (BM25 FTS + vector ANN)  →  scope prefilter  →  rerank  →  top-k passages
   │
   ▼
resolve citations deterministically (passage → source_note anchor)  →  LLM synthesizes the cited answer
```

### Indexing rules (these are where vector stores rot — get them right)
- **One shared table, scoped by a field** — not one index per scope. Add `scope`/`mentor`, `note_type`, `kind` columns; filter with a `WHERE` prefilter. Verified-clean prefilter = no cross-scope bleed, and adding a new scope needs zero new infra.
- **Batch upsert, then `optimize()`.** Per-row `merge_insert` fragments the index (LanceDB grows fragments → ANN degrades). Write in batches and compact when fragments approach the ceiling (~50). This single rule prevents the most common "my RAG got slow" failure.
- **Body-only content hash for change detection.** Hash the note *body*, not the whole file — so a frontmatter stamp (status flip, a new theme) does NOT trigger a needless re-embed. Re-embed only when the meaning changed.
- **Incremental, not rebuild-the-world.** Index new/changed notes; leave the rest. Make the indexer idempotent so reruns are safe.
- **Index the atomic layer; keep raw as the citation target.** You retrieve ideas (atomic) and cite locations (raw anchors).

### Querying rules
- **Hybrid > pure vector.** Combine lexical (BM25/FTS) with semantic ANN; rerank the union. Pure-vector misses exact-term queries; pure-lexical misses paraphrase.
- **Prefilter on scope before the vector search**, not after — post-filtering throws away recall budget.
- **Resolve citations programmatically**, mapping each retrieved passage back to its `source_note` anchor, and hand the LLM passages *with* their citations attached. The model quotes; it does not get to invent provenance.
- **Return JSON for orchestration.** A `--json` mode (passages + citations + scores) lets an outer agent (e.g. Claude Code) compose the final voiced/cited answer.

## The "chat with my vault" contract
Grounded retrieval is necessary but not sufficient — the answer layer needs guardrails (ground-or-abstain, mandatory citation, labeled extrapolation). Those live in `cartography-and-personas.md`.
