# Why AI Playlist beats JoVE Labs at picking videos

Read-only comparison of the **AI Playlist** agentflow (Flowise, `bd799a71-9b90-4bdd-888e-627e3428fa55`, 28 nodes) against the **JoVE Labs** module-generation code in `research-svc`. No prediction endpoints were called; nothing was written to Flowise.

---

## The short answer

The playlist is not better because it has a smarter model or a better prompt. It is better because of the **shape of the retrieval step**. Three things, in order of how much they matter:

1. **The playlist decomposes before it searches, and searches many times.** One user topic becomes 10–20 short, distinct, LLM-generated subtopic queries fired in parallel. Labs sends **one query per method**, and that query is a long, over-qualified string the extraction LLM wrote for a different purpose.
2. **The playlist over-fetches by 5–20x and lets an LLM throw most of it away.** It pools up to 100–480 candidates and keeps 20. Labs' best path pools ~20 per method; Labs' full-lab path pools **6 and keeps all 6, with no LLM filter at all**.
3. **A single bad query cannot poison a playlist.** With 10–20 queries competing into one pool, one junk keyword contributes 5–10% of candidates and the curator outvotes it. In Labs, one bad query *is* 100% of that method's candidate pool — the curator has nothing better to choose from, and the prompt telling it to "drop off-topic videos" cannot help, because everything in front of it is off-topic.

Everything else — the prompts, the dedupe, the ID whitelist, the article-type preference — Labs has already largely copied and they are roughly at parity. The gap is retrieval breadth and query construction.

---

## Correction to the premise: it is not the same backend

You said both use the same search backend. Half true, and the half that differs matters.

| | Endpoint | Ranking |
|---|---|---|
| AI Playlist | `POST /api/free/search/search_ai` | AI/Pinecone semantic path |
| Labs — preview, single-module curate, method refresh | `POST /api/free/search/search_ai` | same as playlist |
| Labs — **full-lab `generateCurriculum`** | `POST /api/free/search/search_es` | Elasticsearch / lexical |

Both send `override_query: true`, i.e. both **opt out of the backend's own query rewriting and expansion**. The playlist compensates for that by doing the expansion itself in an LLM node. Labs opts out and then does not compensate. That is the single most consequential line of configuration in this comparison.

Also: the playlist sends `Authorization: Bearer <user token>` and **drops every row where `isSubscribed` is false**. Labs' search calls are unauthenticated (`Content-Type` only) and never filter on subscription — subscription flags are attached *afterwards*, for UI gating, in `labs.service.ts` (~L446–501). So a Labs module can legitimately be built out of videos the trainee cannot watch. Some "off-topic" complaints are probably "locked/irrelevant to me" complaints wearing a disguise.

---

## Side by side, with the real numbers

### AI Playlist

**Flow:** Start → fetch profile → access check → validate input → *(clarify if ambiguous)* → **plan** → validate readiness → route → **subtopic generation** → **fan-out search** → **LLM curation** → **rehydrate + enforce + build response** → save.

- `llmAgentflow_1` "Analyzing your Topic..." — turns the topic into `search_keywords`. Hard rules in the prompt: **max 5 words each**, canonical academic terminology, distinct and non-overlapping, no filler ("overview", "basics", "of physics"), ordered foundational → advanced. Max 10 keywords for a new playlist, 20 when growing one.
- `customFunctionAgentflow_1` "Searching JoVE library..." — the retrieval engine:
  - `buildSearchQueries()` = `[topic, ...parser keywords, ...state keywords]` plus **word-truncated variants** (a 3+-word keyword also gets searched as its first 2 words), deduped, sliced to the cap.
  - Two policies: `initial_limited` (10 queries × `per_page` 10 = **≤100 candidates**) for a plain first create; everything else 20 queries × `per_page` 24 = **≤480 candidates**.
  - All queries fire **in parallel** (`Promise.all`), 40s timeout each, per-query failures are swallowed and logged rather than failing the run.
  - `category_filter` is **role-gated**: base is `business, jove_core, science_education, lab_manual`; `journal` + `encyclopedia_of_experiments` are added only for research-ish role labels (postdoc, PI, lab tech, etc.).
  - Dedupe by article id **and** by an aggressively normalised title key, with a preference score on collision: `jove_core` 3 > `science_education`/`jove_education` 2 > everything else 1, tie-break lower article id.
  - Candidates are **compacted to `{id, t, ty}`** before the LLM sees them — no descriptions, no images. Cheap enough that 480 candidates fit in one call.
  - Emits a structured `curation_context`: `mode` (`new` | `append` | `recalibrate`), `requested_count` / `target_count`, `must_keep_ids`, `new_slots`, `existing_labels`, `existing_article_ids`, `candidates`.
- `llmAgentflow_2` "Organizing playlist..." — one call, mode-aware, selects and labels and sequences. Selects ~20 from up to 480.
- `customFunctionAgentflow_2` "Building curated response..." — the enforcement layer. **Rehydrates** each returned `{id,t,ty}` against the candidate map so the real title/`articleType`/`headerImage` come from the search result and never from the model. `requireCandidateMembership: true` on the recalibrate paths hard-rejects any id not in the pool. Trims to the requested count. Honours `must_keep_ids` even when that means exceeding the target on a grow. Tops up from the existing draft when the model under-delivers on a shrink.
- Shortfall is **surfaced to the user**, not hidden: "I found 12 videos out of 20 requested." Deliberately suppressed when 20 was the system default rather than a user ask.

### JoVE Labs

**Flow:** researcher → publications → `extractTechniquesFromPublications` → *(optional Confirm Modules preview)* → generate.

Two live retrieval paths, and which one you get depends on whether the request carried confirmed modules (`labs.service.ts` ~L1006–1020):

**Path A — request has `modules[]` (the Confirm-Modules flow). This is the good one.**
`buildCurriculumFromConfirmedModules` → `enrichModulesWithCuratedVideos` → `curateSingleModuleVideos` → `searchMethodCandidates`.
- **One query per method**, the raw `technique.searchTerm`, verbatim.
- 2 category-filtered `search_ai` calls (Concept, Experiment), `per_page` **10** each → ≤20 raw rows per method, minus text-only drops and dedupe.
- Candidates compacted to `{id, title, articleType}`, grouped per method, handed to Luna with the `MODULE_VIDEO_CURATION` prompt.
- Post-LLM: real ID whitelist (`candidateById.get(id)`), claim sets for id and title, throws if the model returns nothing usable. **This part is genuinely good and matches the playlist.**

**Path B — no `modules[]`. `generateCurriculum` → `enrichModulesWithVideos` → `matchModuleVideos`. This is where off-topic comes from.**
- **One query per module**, built as `module.name + ' ' + searchTerms.join(' ')` — a 30–50 word bag of words. For a module merging three methods that is something like
  `"Confocal Imaging of Neural Tissue Fluorescence Confocal Microscopy of Fixed Tissue Sections Immunohistochemical Staining of Mouse Brain Slices Stereotaxic Injection in Adult Mice"`.
  Against a lexical `search_es` with `override_query: true`, any single strong token in that soup can carry an unrelated video to the top.
- Endpoint is **`search_es`**, not `search_ai`.
- `topK` 30 but `per_page` **3** → **≤3 rows per bucket, ≤6 per module.**
- **No LLM curation whatsoever.** Whatever the search returns first is what the trainee sees.
- No relevance floor. `relevanceScore` is parsed, carried, and persisted, and **never used as a filter anywhere in `src/labs/`** (verified by grep).
- `MODULE_MIN_VIDEOS = 1`. A module with one weak video passes every availability gate in the codebase.
- `matchModuleVideos` also never got the `jove_core`-preference dedupe that `searchMethodCandidates` has — on a title collision it keeps whichever bucket returned first.

There is also a `Promise.allSettled` in both matcher methods that swallows a failed category search silently — a Concept-search timeout yields an Experiment-only module and only a `logger.warn`.

---

## The gap in one table

| Mechanism | Playlist | Labs Path A | Labs Path B |
|---|---|---|---|
| Query decomposition before search | 10–20 LLM subtopics, ≤5 words each | none | none |
| Queries per retrieval unit | 10–20 (+ truncated variants) | 1 per method | 1 per module |
| Query text | short, canonical, distinct | long qualified `searchTerm` | all method terms concatenated |
| Endpoint | `search_ai` | `search_ai` | **`search_es`** |
| Candidate pool | 100–480 | ~20 per method | **≤6 per module** |
| Over-fetch ratio (pool : kept) | 5:1 – 20:1 | ~4:1 – 13:1 | **1:1** |
| LLM curation | yes | yes | **no** |
| ID whitelist after LLM | yes | yes | n/a |
| Rehydrate metadata from search result | yes | yes (candidate object reused) | n/a |
| Subscription filter at search time | **yes** | no | no |
| `category_filter` gated by audience | yes (role-based) | no (always both buckets) | no |
| Relevance floor | no (curation substitutes) | no | **no, and nothing substitutes** |
| Shortfall surfaced to user | yes, with counts | partially (`unmappedTechniques`) | no |
| Clarify before searching an ambiguous topic | yes, blocking | no | no |

---

## What to actually copy, ranked

### 1. Decompose the search term into 3–6 short queries per method, and fan out
This is the whole ballgame. Right now a method contributes exactly one query. Copy `buildSearchQueries()` from the playlist node: take the `searchTerm`, and also search the short `name`, and also the first two words of each. That is a handful of lines and turns 1 query into 3–5 without any new LLM call.

If you want the full playlist behaviour, add a subtopic-generation step between technique extraction and search, with the playlist's exact constraint set: **≤5 words, canonical terminology, distinct, no filler**. Note that Labs' extraction prompt currently pulls in the *opposite* direction — it explicitly asks for searchTerms "anchored to the organism, cell type, specimen, substrate, dataset, model family, or experimental condition", producing things like `"Neural Radiance Fields for MRI Volume Reconstruction"`. That is an excellent *label* and a poor *query*: against a lexical index it recruits every MRI video in the catalog. **Keep `searchTerm` for display and provenance; derive short query strings from it for search.**

### 2. Raise the candidate pool, then let the curator cut
`METHOD_CANDIDATES_PER_CATEGORY = 10` carries the comment *"Matches playlist search_ai per_page."* That comment is the source of the error. The playlist's `per_page` is 10 only in its narrowest `initial_limited` mode; every other mode uses **24**, and the playlist multiplies that by 10–20 queries. Labs multiplies 10 by **one**. Copying a scalar from a fan-out system into a single-shot system silently reproduced 5% of the pool.

Take `per_page` to ~24 and combine with fan-out from item 1. The curation LLM is already cheap because candidates are compacted — this is a token-budget change, not an architecture change.

### 3. Give Path B the same treatment as Path A, or delete Path B
`generateCurriculum` → `enrichModulesWithVideos` → `matchModuleVideos` is a `search_es`, 6-candidate, zero-curation path that still runs in production whenever a generate request arrives without `modules[]`. Either route it through `enrichModulesWithCuratedVideos` like the confirmed-modules path does, or establish that no client can reach it and remove it. **Also stop concatenating the query**: send one search per method the way `searchMethodCandidates` does, never `name + all terms joined`.

### 4. Copy the subscription filter into the search step
The playlist drops `!isSubscribed` rows before the LLM ever sees them. Labs builds modules from anything and gates in the UI later. Passing the trainer's token to `search_ai` and filtering at retrieval removes a class of complaint that reads as "off-topic" but is really "I can't watch this."

### 5. Surface the shortfall
The playlist says "I found 12 out of 20 requested." Labs silently ships a 1-video module (`MODULE_MIN_VIDEOS = 1`) and looks confidently wrong. Either raise the floor or say the number out loud. A stated shortfall is a much smaller support ticket than a bad suggestion.

### 6. Copy the two cheap correctness details
- **Aggressive title normalisation.** Playlist `normalizeDuplicateTextKey` strips *all* non-alphanumerics including whitespace, so `"Cell Culture: Part 1"` and `"Cell Culture Part 1"` collide. Labs `normalizeMatchedVideoTitle` only lowercases and collapses whitespace, so they don't. Three lines.
- **`jove_core` preference on Path B.** `searchMethodCandidates` already has the preference score; `matchModuleVideos` doesn't. Lift the function.

### 7. Optional: clarify before searching
The playlist's planner (`llmAgentflow_0`) blocks and asks one question on a polysemous topic ("cell" → biological or electrochemical?). Labs has no equivalent — it takes whatever the extraction LLM produced and runs. Lower priority, because Labs' input is a published paper rather than a free-text topic, so ambiguity is rarer. Worth having for the trainer-edits-methods flow.

---

## What not to copy

- **The stateful mode machine.** `curation_context.mode` (`new`/`append`/`recalibrate`), `must_keep_ids`, `new_slots`, the count arithmetic in `resolveCountRequest`, `trimDraftToCount`, `makeRecalibratedDraft`. That complexity exists because the playlist is a multi-turn chat over a mutable draft. Labs generates once from a paper. Porting it buys nothing and costs a lot.
- **`override_query: true`.** Both sides already send it. Don't propagate it further — and it is worth a deliberate experiment to send `override_query: false` on the Labs side and see whether the backend's own query understanding fixes half of this for free.

---

## The specific checks to run on the Labs side

Ordered by expected signal per unit of effort. All paths are absolute.

1. **Which path is actually serving the complaints.** Turn up the two log lines that already exist and diff them against complaint reports:
   - `search_es: N result(s) for "<query>" — video ids: [...]` — `~/dev/jove-code/research-svc/src/campaigns/services/jove-api.service.ts:222`
   - `search_ai: N video(s) for "<query>" (dropped M text-only)` — same file, L279
   If complaints correlate with `search_es` lines, item 3 above is the entire fix. If they correlate with `search_ai`, it is items 1 and 2.

2. **Read the actual query strings in the logs.** `matchModuleVideos` logs `query="<first 80 chars>"` at `~/dev/jove-code/research-svc/src/labs/services/ai/module-video-matcher.service.ts:235`. Eighty characters is not enough to see the concatenation problem — raise the slice temporarily. You are looking for module-name-plus-every-method soup.

3. **Confirm the deployment seam.** Several call sites branch on `typeof this.moduleVideoMatcher.searchMethodCandidates === 'function'` (`curriculum-generator.service.ts` L372, L518, L668, L815; `modules.service.ts` L1371). These are described in comments as test/compat seams, so in a normal build the curated path should always win. **Verify that in the running pods** — if any environment has an older `ModuleVideoMatcherService`, that environment is silently on the uncurated `search_es` path for everything.

4. **Instrument the pool size, not just the output.** Log `candidateById.size` next to selected count in `previewVideoFirstModules` (`curriculum-generator.service.ts` ~L395) and `curateSingleModuleVideos` (~L552). If the pool is ~10–20 and the model keeps 8, the curator has no room to be selective and no prompt change will fix it.

5. **Check the `category_filter` slugs against the real API.** `VIDEO_CATEGORY_FILTERS` in `~/dev/jove-code/research-svc/src/labs/entities/lab-module-video.entity.ts:46` uses `lab_manual_procedure`. The playlist uses **`lab_manual`**. They cannot both be right. If Labs' slug is wrong, `search_ai` may be silently narrowing or ignoring the filter — and that alone would explain off-topic Concept results. The file's own comments already flag slug fragility (the `research` vs `journal` alias note at L23–45). Fastest check in this whole list.

6. **Decide whether `journal` + `encyclopedia_of_experiments` belong in every Labs module.** The playlist gates those two behind a research-role check; Labs always includes them in the Experiment bucket. Defensible for a researcher-facing product, but if trainees are junior it is a direct source of "this is a research paper, not training." Note also that `science_education` sits in Labs' Experiment bucket while the shared preference score treats it as concept-tier — those two classifications disagree.

7. **Decide what to do with `relevanceScore`.** It is parsed at `module-video-matcher.service.ts:128–135`, carried through every DTO, persisted on `lab_module_videos`, and **never read as a filter**. Either use it as a floor on the uncurated path or stop pretending it does anything.

8. **Make a silent category failure loud.** Both matcher methods use `Promise.allSettled` and only `logger.warn` when a bucket fails (`module-video-matcher.service.ts:205–211` and `288–294`). Count these. A module that quietly became Experiment-only because a Concept search timed out looks exactly like an off-topic module to a trainer.

9. **Reconsider `MODULE_MIN_VIDEOS = 1`** (`~/dev/jove-code/research-svc/src/labs/module-min-videos.util.ts`). It is the gate for full-lab generate, single-module generate, preview split, and `check-module-videos`. At 1, every availability check in the product is effectively disabled.

---

## Caveats

- Everything above is read from source and from the stored Flowise flow definition. **No flow was executed and no search was run** — the pool sizes and query shapes are derived from the code, not observed in production. Items 1, 2, and 4 in the checklist are how you confirm them empirically.
- Both systems call the same model id (`gpt-5.6-luna`). Labs passes `reasoningEffort: 'none'` on both curation calls; the playlist leaves temperature and the rest of the model config unset. Model choice is not the differentiator here, but if you want one more free lever, `reasoningEffort: 'none'` on a "drop the off-topic ones" judgment is worth an A/B.
- `enrichModulesWithMethodCandidates` (`curriculum-generator.service.ts:1309`) is marked unused and `enrichModulesWithVideos` is reachable only via `generateCurriculum`. Confirm both against live traffic before deleting either.
- The Flowise instance holds 18 agentflows; `AI Playlist` is the only one relevant here. All 18 report `deployed: false`, which is a Flowise-internal flag and does not tell you whether the flow is reachable via API — I did not attempt to determine that, since it would have required calling a prediction endpoint.
