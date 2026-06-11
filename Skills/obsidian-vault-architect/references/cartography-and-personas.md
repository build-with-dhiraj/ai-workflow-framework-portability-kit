# Cartography & Persona/Voice Fidelity

Two layers that sit on top of a retrieval-ready vault: **cartography** (auto-generating the theme map humans browse) and — for "chat with my vault / consult a voice" vaults — **persona fidelity guardrails** that keep answers honest.

## Cartography: generating the theme map

Atomic notes give you precision but no overview. Cartography clusters them into themes and writes **Maps of Content (MOCs)** so the corpus is navigable by humans and an LLM alike.

### LLM-clustering vs. code-graph tools (a decided bake-off)
Two families were compared for organizing **prose** notes:

- **Semantic LLM-clustering** (embed atomic notes → cluster → an LLM names each cluster and writes its MOC). **Winner for prose.** It groups by *meaning*, names themes the way a human would, and writes directly into the vault as markdown MOCs. No auth, no external service, works on natural-language notes.
- **Code-graph / static-analysis graph tools** (e.g. Graphify-style). Built to graph **codebases** (imports, symbols, call edges) — explicitly *anti-vector*, and auth-gated/awkward on prose. Wrong tool for a knowledge vault of essays and transcripts.

**Rule:** for a prose knowledge vault, use **LLM-clustering** for cartography. Reach for code-graph tooling only when the "vault" is actually source code.

### Cartography process
1. Embed the atomic notes (reuse the retrieval index).
2. Cluster (k chosen by silhouette/elbow or an LLM pass over `_index.md`).
3. For each cluster, an LLM writes a **theme MOC**: a 1–2 line definition + wikilinks to its member atomic notes, frontmatter `note_type: moc`, scope key, `themes`.
4. Write MOCs to `_moc/themes/`; reflect the theme map back into any persona card's "recurring frameworks."
5. Regenerate incrementally as new atomic notes land — don't rebuild from scratch each time.

## Persona / voice fidelity (only for "consult a voice" vaults)

If the vault is consulted as a **person/voice/advisor** ("ask my notes in X's voice"), grounded retrieval is necessary but not sufficient. Without guardrails the model will smooth a real, sourced voice into generic LLM mush, or fabricate positions the source never held. These are the **PersonaCite** guardrails — apply them in the answer layer (system prompt + orchestration), not the vault:

1. **Ground-or-abstain.** Answer only from retrieved passages. If the source never addressed it, the seat says "hasn't spoken to this" — it does NOT improvise a plausible take.
2. **Citation-mandatory.** Every claim carries its source + anchor, resolved deterministically before generation (see retrieval-architecture). Quotes are quoted; provenance is not the model's to invent.
3. **Labeled extrapolation.** When the user wants advice beyond the literal corpus, mark the boundary: *cited* vs *inference-from-their-principles* must be visibly distinct, never blended into one confident voice.
4. **Per-voice isolation.** Each voice retrieves ONLY from its own scope (the `WHERE scope` prefilter). No bleed — voice A never answers from voice B's notes.
5. **Preserve contradictions, don't average.** If a voice held tension (or two voices disagree), surface both positions attributed — never blend into a mean that's true to neither.
6. **"Reconstruction, not the person."** Frame the seat as a grounded reconstruction from public material, not the actual human. Honesty about the artifact.

### Persona card
A per-voice `personas/<scope>.md`, **human-reviewed before going live**, holding:
- standing framing ("reconstruction, not the person"),
- voice + a few verbatim anchors (how they actually talk),
- signature frameworks/recurring themes (from cartography),
- **coverage & gaps** — what the corpus does and doesn't cover, so the seat knows its own edges.

### Multi-voice "roundtable" (optional)
When several voices are consulted together: each answers grounded+cited in its own voice → rebuttals are grounded **only** in the rebutting voice's own notes (never invented) → a neutral "chair" maps agreements/tensions, **attributed, never blended**. A voice with too little coverage on the topic abstains rather than padding.

## Where this fits the build checklist
- Cartography is a follow-on after a scope's atomic notes + index exist.
- Persona guardrails are required *before* a "consult a voice" vault is used for anything real — they're the trust contract, not a nicety.
