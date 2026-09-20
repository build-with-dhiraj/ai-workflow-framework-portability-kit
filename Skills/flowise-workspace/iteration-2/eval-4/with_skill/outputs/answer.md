# Why AI Playlist beats JoVE Labs at picking videos — and what to actually copy

**Read date:** 17 Aug 2026.
**Playlist source:** Flowise agentflow `AI Playlist`, id `bd799a71-9b90-4bdd-888e-627e3428fa55`, 28 nodes, created 2026-04-20, last updated 2026-08-17 (the day of this read). Read-only; no prediction endpoint called.
**Labs source:** `~/dev/jove-code/research-svc`, `src/labs/`.

---

## The short answer

The playlist is not better because of a better prompt, a better model, or a richer payload. On those three it is either identical to Labs or worse.

It is better because of **breadth of retrieval and a willingness to refuse**:

1. **It turns one topic into 10–20 deliberately non-overlapping search queries and pools all the results into one candidate set.** Labs turns one technique into one query and keeps each technique's results in its own silo. The playlist's curator picks 20 videos out of ~100–480 candidates; Labs' curator picks 3–10 out of ~20 that it is forbidden to compare against a sibling method's. Same model, same three fields per candidate — but one has a competitive pool and the other does not.
2. **It refuses.** When nothing good comes back the playlist says "we couldn't find any videos on that topic, want to try a different one?". Labs' entire definition of success is `MODULE_MIN_VIDEOS = 1` — one row came back, ship it. Labs also *captures* JoVE's own `relevanceScore` on every candidate and then never compares it to anything.
3. **It asks before it searches.** A polysemous topic triggers a clarification question instead of a search. Labs never asks about a technique.

The one thing you should not spend a sprint on is enriching the candidate payload. **Both systems hand the model exactly the same three fields.** Details in "The false lead" below.

---

## The verified comparison

Every row is a claim about code I read. Where I could not verify something, the row says so.

| Layer | AI Playlist | JoVE Labs | Verified in |
|---|---|---|---|
| **1. Input** | Typed topic + page context (`page_context`, `page_info`, `current_article_id`, `current_article_content`) + UI-selected videos | Researcher's publications → **title + abstract only** | Playlist: Start node `startState`. Labs: `curriculum-generator.service.ts:1142-1150` |
| **2. Normalisation** | **Unconditional.** One LLM node converts topic → ≤10 keywords (≤20 with an existing draft), each ≤5 words, distinct and non-overlapping, ordered foundational→advanced | **None.** A dictionary lookup swaps display `name` for the LLM-authored `searchTerm`, falling back to the raw string on a miss. No expansion on any path | Playlist: only edge into the search node is `llmAgentflow_1 -> customFunctionAgentflow_1`; prompt "Analyzing your Topic…". Labs: `lab-module-techniques.util.ts:182-196` |
| **3. Queries issued** | **10 queries × 10 results** (first create) or **20 × 24** (detailed / expand / explicit count), fired in parallel, then pooled and deduped by `articleId` → **≤100 or ≤480 candidates for the whole playlist** | **2 calls per technique** (one per category bucket), same query string in both, `per_page: 10` → **≤20 candidates per technique**, never pooled across techniques | Playlist: `MAX_INITIAL_SEARCH_QUERIES=10`, `DEFAULT_SEARCH_RESULTS_PER_KEYWORD=10`, `MAX_SEARCH_QUERIES=20`, `MAX_SEARCH_RESULTS_PER_KEYWORD=24`; `buildSearchQueries` + `Promise.all`. Labs: `module-video-matcher.service.ts:90-103`, `:267-276` |
| **4. Backend** | `POST /api/free/search/search_ai`, `override_query: true`, **with `Authorization: Bearer`**, then hard-drops every `!isSubscribed` candidate | `search_ai` on 5 of 6 entrypoints — **but `search_es` (keyword) on full-lab auto-generate and on every fallback**, with a single space-concatenated query. **No `Authorization` header on either** | Playlist: search node l.789-805, l.863. Labs: `jove-api.service.ts:242-289` (ai) vs `:181-232` (es); `module-video-matcher.service.ts:153-160` `buildQuery` |
| **5. Payload per candidate** | `{ id, t, ty }` = articleId, title, articleType | `{ id, title, articleType }` | Playlist: `compactCandidate`. Labs: `curriculum-generator.service.ts:389-393`, `:546-550` |
| **6. Instruction** | PhD SME; select, label, sequence; "select all relevant available candidates" if fewer exist; "do not try to create a comprehensive playlist unless the requested count is large enough" | PhD curriculum designer; "Drop off-topic, near-duplicate, or weaker videos"; "**Do not pad with weak or off-topic videos to hit a count**"; "Fewer than 3 is fine" | Playlist: "Organizing playlist…" prompt. Labs: `prompt-keys.ts:143-174`, `:193-211` |
| **7. Output contract** | Flowise **declared structured output** on every LLM node; ids re-hydrated from a candidate map, non-member ids dropped, count enforced by `trimDraftToCount` | Raw `JSON.parse` + unchecked `as T`; hand-rolled shape checks. Hallucinated ids **are** dropped via `candidateById` lookup | Playlist: `llmStructuredOutput` per node; `buildCandidateMap` / `hydrateVideo` / `dedupeArticles(requireMembership)`. Labs: `openai.service.ts:106-130`; `curriculum-generator.service.ts:453-455`, `:592-594` |
| **8. Refusal / floor** | `NO_RESULTS`: "Sorry, we couldn't find any videos under your subscription on X… Want to try a different topic?" Shortfall copy: "I found N videos out of M requested" — and deliberately suppressed when the count was a system default, not a user ask | `MODULE_MIN_VIDEOS = 1`. Refuses only at **zero** (`NO_VIDEOS_FOR_METHODS_MESSAGE`). `relevanceScore` persisted, **never compared**. `curriculumConfidence` persisted, **gates nothing** | Playlist: curated-response node l.1050, l.1121-1122, l.1143. Labs: `module-min-videos.util.ts:7`; `lab-module-video.entity.ts:102`; `curriculum-generator.service.ts:1591-1625` |
| **9. Disambiguation** | 10 clarification kinds incl. `topic_domain` ("cell" = biological vs electrochemical) and `content_shortfall`; asks exactly one question; a second LLM classifies the reply and **prefers `unclear` over guessing**. When readiness is `needs_clarification`, `validated_route ≠ TOPIC_SEARCH`, so **no search runs at all** | **None at the technique or video layer.** (It exists at the *researcher* layer — see the inversion below) | Playlist: "Planning request & clarifications…" prompt; "Resolving your answer…" prompt; `conditionAgentAgentflow_0` conditions. Labs: `researcher-search.service.ts:74-346` only |
| **10. Model** | `gpt-5.6-luna` on all 6 LLM nodes | `OPENAI_MODEL` env, **repo default `gpt-4o-mini`**; curator runs at `reasoningEffort: 'none'`. Live value NOT VERIFIABLE from the repo | Playlist: `llmModelConfig.modelName`. Labs: `openai.service.ts:33`; `curriculum-generator.service.ts:428-430`, `:579-581` |
| **11. Feedback loop** | Every custom-function node returns a `_debug` envelope — decisions, per-call `method/url/body/status/elapsed_ms/query/raw_items_count`, timings — with tokens scrubbed. Generated from `nodeDebug.js` by `buildAgentflow.py`, i.e. the flow is built from version-controlled source | Query logged truncated to 80 chars. `search_ai` logs **result count but not ids**. Curator input and output **never logged**. No trace id, no metric, no telemetry, **no user-feedback capture on a suggested video** | Playlist: `buildNodeDebug` header on every code node; `metricsOut.api_requests`. Labs: `module-video-matcher.service.ts:234-236`, `:328-330`; `jove-api.service.ts:221-223` vs `:278-280` |

---

## What specifically makes the playlist better

Ranked by how much of the "off-topic" complaint each one explains.

### 1. Query fan-out and candidate pooling (the big one)

The playlist's chain is: **one topic → LLM writes 10–20 non-overlapping subtopic queries → all fired in parallel → all results pooled and deduped into one candidate list → one curation decision over the whole pool.**

The keyword prompt is explicitly tuned to maximise coverage rather than paraphrase: keywords must be "distinct and non-overlapping", must not be "duplicate, near-duplicate, or wording-only variations", must not be "generic variants that only rephrase the main topic". `buildSearchQueries` then adds truncated two-word prefixes of multi-word terms as extra recall. The raw topic is always kept as a query too, so if the keyword LLM returns nothing the flow degrades to a plain search instead of breaking.

Labs' chain is: **one technique → one query string → 2 category calls → ≤20 candidates → curator may only pick from that technique's own bucket** ("Pick videos only from that method's own candidates", `prompt-keys.ts:149`).

Two consequences, both of which look exactly like "off-topic suggestions" to a user:

- **Shallow pool.** If a technique's 20 candidates are all mediocre, the curator's only choices are mediocre videos or dropping the method. The prompt's "Aim for 3–10 videos per module when that many candidates are relevant" then biases toward filling.
- **No substitution.** A genuinely better video for method A that happened to surface under method B's search is invisible to the curator. The playlist has no such wall — its pool is flat.

The playlist's own worst path illustrates the same point in reverse: full-lab auto-generate in Labs (`search_es`) concatenates the module name and every technique term into **one** bag-of-words string and asks for 3 results per bucket. That yields ≤6 candidates for an entire module from a query that is the centroid of several unrelated concepts, with **no curator at all** — `attachMatchedVideos` (`curriculum-generator.service.ts:1546-1559`) writes raw search output straight onto the module.

### 2. A relevance floor, and permission to under-deliver

Both prompts tell the model not to pad. Labs' wording is arguably stronger than the playlist's. That is precisely the signal that the gap is not in the prompt — an instruction with no enforcement behind it is a request.

The playlist enforces in code: `trimDraftToCount` and `keepSet` cap the output, `requireMembership` drops non-candidates, and `NO_RESULTS` is a real terminal state with copy that sends the user back to pick a different topic. It even distinguishes a user-requested count from a system default so it does not apologise for a shortfall nobody asked about.

Labs enforces one thing: at least one video exists. `relevanceScore` — JoVE's own ranking signal, already parsed at `module-video-matcher.service.ts:128-135` and already persisted at `lab-module-video.entity.ts:102` — is never read by any comparison anywhere in the service. So is `curriculumConfidence`.

### 3. Asking instead of guessing

The playlist's planner treats ambiguity as a first-class outcome: `readiness ∈ {ready, needs_clarification, unsupported}`, ten named clarification kinds, and a hard rule that a clarification suppresses the search entirely. Its resolver prompt ends with the reasoning: *"Prefer unclear over guessing. A re-asked question is much cheaper than a wrong playlist mutation."*

Labs never asks about a technique. Worth noting how it fails, though — Labs is a generate-then-review flow, not a chat, so "ask exactly one question mid-flight" may not fit the product. The Labs-shaped equivalent is marking a technique low-confidence in the review UI rather than blocking on it.

### 4. Instrumentation, which is why the playlist got tuned at all

The playlist flow is generated from source by `buildAgentflow.py`, and every code node carries a `buildNodeDebug` envelope recording the decisions taken, every HTTP call with its body and query and `raw_items_count`, and per-stage timings. It was created 20 Apr 2026 and edited the day I read it. Four months of iteration against visible per-request evidence is the actual origin of its quality, and that is the one thing you cannot copy as text.

Labs cannot currently answer "why was this video suggested to this module?" The persisted row keeps `relevanceScore` but not the query, not the technique it matched, not whether a curator chose it or a raw search attached it, and not which retrieval path served the request. On the primary path the ids returned by `search_ai` are never logged and the curator's selection is never logged at all.

---

## The false lead: do not enrich the candidate payload

This is the trap this comparison is designed to catch, and it is worth stating flatly because it is where a sprint would otherwise go.

```js
// AI Playlist — search node
function compactCandidate(video) {
  return { id: Number(video.articleId), t: String(video.title || ""), ty: video.articleType || null };
}
```

```ts
// JoVE Labs — curriculum-generator.service.ts:389-393
candidates: (candidateResults[index] ?? []).map((video) => ({
  id: video.videoId,
  title: video.title ?? '',
  articleType: video.articleType,
})),
```

**Three fields each, and the same three fields.** Both systems deliberately withhold what they have: the playlist discards `excerpt` (its `normalizeVideo` populates it) and its curation prompt explicitly forbids `headerImage`, `isSubscribed`, `metrics`, `isNew` and profile fields; Labs discards `description` and `relevanceScore`.

The reason the playlist can afford to be this thin is the same reason it works: minimal candidates are how you fit 480 of them in one context window and still get a comparative judgment. Depth per item is traded for breadth of pool, on purpose.

So: adding `description` to the Labs payload is a defensible small experiment, but it cannot be the explanation for the complaints, because the system that works well does not have it either. The one field genuinely worth extracting from that list is `relevanceScore` — not to show the model, but to filter on before the model ever sees the candidate.

---

## The inversion worth noticing

Labs starts from a researcher's actual publications. That is a far richer seed than a typed topic. If the richer-input system produces worse output, the extra context is being thrown away somewhere — and it is:

- **Only title and abstract reach the extraction LLM.** `authors`, `doi`, `pmid`, `year`, `journal` and `keywords` are all parsed by `publication-parser.service.ts` and then dropped at `curriculum-generator.service.ts:1142-1150`.
- **The qualified search term is computed and then discarded.** Extraction produces a genuinely good artefact — `searchTerm`, "anchored to the organism, cell type, specimen, substrate, dataset, model family, or experimental condition from the paper" (`prompt-keys.ts:80-81`), e.g. *"Fluorescence Confocal Microscopy of Fixed Tissue Sections"*. It is written to `technique_search_terms` in four places (`labs.service.ts:850`, `:1127`, `modules.service.ts:474`, `:1458`) and **read back in zero places**. So the refresh-videos endpoint regresses the query from that qualified phrase to the bare display name *"Confocal Microscopy"*.
- **The disambiguation instinct already exists one layer up.** `researcher-search.service.ts` refuses to guess a person: *"a wrong person is never returned in place of a match"*, returning 400 with "Several researchers publish under that name. Add their institution or an ORCID iD." The team already knows how to do this. It just isn't applied to techniques.

Labs' problem is not a missing recipe. It is that the best asset it has — paper-anchored, qualified method names — is being narrowed to one shallow search and then partly thrown away.

---

## What to go and check on the Labs side

Ordered by value per hour. The first four are checks, not builds.

### Check 1 — Is the silent fallback firing in production? (do this first)

`curriculum-generator.service.ts:321` is an **unqualified** `catch (error)` around `previewVideoFirstModules`. Any failure inside it — a `search_ai` timeout, a JSON parse error, **or the entirely legitimate `BadRequestException(NO_VIDEOS_FOR_METHODS_MESSAGE)` thrown at `:403`** — switches the request from *per-method `search_ai` + curator* to the legacy *concatenated-query `search_es`* strategy. The `logger.warn` at `:324-328` records that it happened but not which of the three causes fired.

Grep production logs for `"using legacy fallback"`. If that line appears at any material rate, some fraction of your traffic is being served by the worse retrieval path, and **no measurement of the primary path can be trusted until you separate them.** The fix is to rethrow `BadRequestException` rather than swallow it, and to log the cause.

Also check the two unlogged `typeof searchMethodCandidates === 'function'` seams at `curriculum-generator.service.ts:662-679` and `modules.service.ts:1394-1403`, which pick the legacy path with no log line at all.

### Check 2 — Query the relevance scores you already have

`lab_module_videos.relevance_score` is populated and never used. One SQL query answers "how off-topic is off-topic", retroactively, with no deploy:

- score distribution across all module videos, and split by `articleType` / category bucket
- the same distribution for modules users complained about vs the rest
- how many modules sit at exactly 1 video (`MODULE_MIN_VIDEOS`)

If the complained-about modules cluster in a low-score tail, a threshold is your cheapest fix and you can pick its value from data rather than guessing.

### Check 3 — What model is actually running, at what effort

`openai.service.ts:33` defaults to `gpt-4o-mini`; the code has a `gpt-5.6` special case so prod may be set higher, but the repo cannot tell you. Read `OPENAI_MODEL` in the deployed environment. The playlist runs `gpt-5.6-luna` for the equivalent judgment.

Separately, the Labs curator is invoked with `reasoningEffort: 'none'` (`curriculum-generator.service.ts:428-430`, `:579-581`). Relevance ranking across 20 candidates is exactly the kind of comparative judgment that effort setting suppresses. Both are config changes, not code.

### Check 4 — Read the live prompts, not the repo ones

Labs prompts are DB-backed: `PromptTemplateService.getTemplate` (`prompt-template.service.ts:58-72`) reads Redis, then the `ai_prompt_templates` row, and only seeds the repo default on first miss. `prompt-keys.ts:20-22` says so explicitly — *"Changing an existing default does not update environments that already have the row."* A SUPER_ADMIN can edit them via `PUT /api/labs/admin/prompt-template/:promptKey`.

**Everything I quoted from `prompt-keys.ts` is the seed, not necessarily what production is running.** Dump the four live rows (`TECHNIQUE_EXTRACTION_*`, `PREVIEW_VIDEO_CURATION_*`, `MODULE_VIDEO_CURATION_*`) before concluding anything about the instruction layer. Note also that `generateModuleStructure`'s prompt is hardcoded at `curriculum-generator.service.ts:1225-1249` and is *not* tunable this way.

### Then build, in this order

**5. Fan out the query.** The highest-impact change, in two parts:
- Have the extraction LLM emit **3–5 query variants per technique** instead of one `searchTerm` — it is already doing the hard part by anchoring to organism and condition. Mirror the playlist's constraints: distinct, non-overlapping, ≤5 words, foundational→advanced.
- **Pool candidates at module level** before curation instead of siloing per method, and relax `prompt-keys.ts:149` accordingly (keep per-method attribution for the UI; drop the wall the curator cannot see past). This is what lets a curator compare rather than merely accept.

**6. Add the floor.** Threshold on `relevanceScore` before the curator sees a candidate, using the value Check 2 gives you. Then decide whether `MODULE_MIN_VIDEOS = 1` is still the bar you want, and treat "no candidate clears the floor" as a refusal with copy modelled on the playlist's `NO_RESULTS` — which sends the user somewhere useful rather than shipping a weak module.

**7. Read `technique_search_terms` back.** Four writes, zero reads. Fixing this alone stops the refresh-videos endpoint from regressing every module to its bare display name.

**8. Instrument before tuning further.** Log, per suggestion: the full query (not truncated to 80 chars), the candidate ids offered to the curator, the ids it returned and rejected, the retrieval path that served the request, and a trace id joining all of it to the persisted row. Add any user-level signal on a suggested video — there is currently none of any kind. The playlist's `_debug` envelope is the working model, and it is generated from source rather than hand-maintained, which is why it survived four months of edits.

Treat this as the precondition for the rest, not a follow-up ticket. The playlist's advantage is four months of visible evidence; Labs cannot currently tell you whether any change you make helps.

**9. Disambiguation, last.** Adapt rather than copy: Labs is generate-then-review, not conversational, so the fit is a low-confidence flag on a technique in the review UI, not a blocking question. The precedent to follow is already in the repo at `researcher-search.service.ts`.

---

## Caveats

- **Live Labs prompt text is not in the repo** (Check 4). Every Labs prompt quote here is the seed default.
- **`OPENAI_MODEL` in production is unknown** from the repo (Check 3).
- **`override_query: true`** is sent by both systems; I could not verify its server-side meaning, as the search backend is not in this repo. It plausibly disables backend-side query rewriting, in which case both systems are opting out of it and it is not a differentiator — but that is inference, not a verified claim.
- **`module-video-matcher.service.ts:79-84` says `matchModuleVideos` is used by "full-lab generation, single-module generation, and the method-edit refresh endpoint … (JVA-29986)".** The call-site trace disagrees: single-module generate and refresh-videos both route through `curateSingleModuleVideos` → `searchMethodCandidates` (`search_ai`). Treat that docstring as stale and the call sites as authoritative.
- **The playlist's `deployed` flag is `false`**, as it is on all 18 flows on this instance — so it is called via the API rather than exposed as a Flowise chatbot. That is normal here and does not indicate anything is off.
- **Flowise itself was archived upstream on 13 Aug 2026** and is read-only. The playlist flow is safe to keep reading, but any plan that involves *extending* it should account for there being no upstream fixes and for pinning `3.1.3` rather than the final `3.1.4`, whose Docker image is reported not to boot on a fresh volume.

---

## Files worth opening yourself

**Playlist (Flowise, read via API):** flow `bd799a71-9b90-4bdd-888e-627e3428fa55`. Nodes that carry the logic: `Analyzing your Topic…` (`llmAgentflow_1`, the keyword step), `Searching JoVE library…` (`customFunctionAgentflow_1`, 42 KB — retrieval, `compactCandidate`, `buildCurationContext`), `Organizing playlist…` (`llmAgentflow_2`, the curation prompt), `Building curated response…` (`customFunctionAgentflow_2`, 53 KB — id re-hydration, count enforcement, shortfall copy), `Planning request & clarifications…` (`llmAgentflow_0`, the 8.3 KB planner).

**Labs:**
- `~/dev/jove-code/research-svc/src/labs/services/ai/curriculum-generator.service.ts` — `:321` the fallback, `:389-393` and `:546-550` the payload, `:1142-1150` the input narrowing, `:1431-1437` the concatenated query, `:1546-1559` the no-curator path
- `~/dev/jove-code/research-svc/src/labs/services/ai/module-video-matcher.service.ts` — `:90-103` the counts, `:153-160` `buildQuery`
- `~/dev/jove-code/research-svc/src/campaigns/services/jove-api.service.ts` — `:181-232` `search_es`, `:242-289` `search_ai`
- `~/dev/jove-code/research-svc/src/labs/services/ai/prompt-keys.ts` — seed prompts
- `~/dev/jove-code/research-svc/src/labs/module-min-videos.util.ts` — the one-line floor
- `~/dev/jove-code/research-svc/src/labs/lab-module-techniques.util.ts` — `:182-196` the raw-string fallback
