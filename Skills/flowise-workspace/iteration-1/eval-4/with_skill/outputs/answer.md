# Why the AI Playlist beats Labs on relevance, and what to actually copy

## Short version

The playlist is not better because of its prompt, its model, or the data it shows the model. On all three it is either identical to Labs or worse. It is better because of **three steps that exist in the playlist graph and have no equivalent in the Labs service**:

1. **It expands one topic into 10–20 sibling search queries before it searches.** Labs issues exactly one query per method. This is the single biggest difference and the most likely cause of your complaints.
2. **It refuses to execute an ambiguous request.** It stops and asks a question instead. Labs has no concept of asking.
3. **It keeps the research corpus out of teaching output unless the user is a researcher.** Labs pulls journal articles into every training module, unconditionally.

There is also a fourth thing, which is not a design difference but a live defect: **Labs' good video-matching path is wrapped in a catch-all that silently falls back to an older, much weaker path.** From the outside a degraded lab looks exactly like a good one.

One correction to the framing in your question: I did not have to stop at the playlist. The Labs logic is readable at `~/dev/jove-code/research-svc`, so most of the "go and check" list below is already checked. I have marked the handful of items that genuinely still need a human.

---

## Stop looking here — these are not the difference

Worth saying first, because these are where a comparison naturally starts and all three are dead ends.

**The payload is not the difference.** Both systems reduce every candidate video to the same three fields before the model sees it.

Playlist, `Searching JoVE library...` (node 04, `customFunctionAgentflow_1`):

```js
function compactCandidate(video) {
  return {
    id: Number(video && video.articleId),
    t: String((video && video.title) || ""),
    ty: (video && video.articleType) || null,
  };
}
```

Labs, `~/dev/jove-code/research-svc/src/labs/services/ai/curriculum-generator.service.ts:389-393`:

```ts
candidates: (candidateResults[index] ?? []).map((video) => ({
  id: video.videoId,
  title: video.title ?? '',
  articleType: video.articleType,
})),
```

Id, title, type. Identical. If anyone proposes a sprint to enrich the Labs payload with transcripts or abstracts to close the gap, that sprint is aimed at a layer that is already at parity. (There is a real, cheap payload win in Labs, but it is the opposite of enrichment — see "What Labs already has and throws away".)

**The prompt is not the difference.** The Labs curation prompt (`prompt-keys.ts:143-174`) is, if anything, better written than the playlist's. It already forbids padding ("Do not pad with weak or off-topic videos to hit a count"), already permits under-delivering ("Fewer than 3 is fine"), already requires selection from that method's own candidates only, and already handles grouping explicitly. The playlist's equivalent (`Organizing playlist...`, node 06) says broadly the same things less crisply. When the weaker system has the better-written prompt, the gap is not in the prompt.

**The search backend is not the difference.** Both call `POST {base}/api/free/search/search_ai` with `override_query: true`. Playlist: node 04. Labs: `~/dev/jove-code/research-svc/src/campaigns/services/jove-api.service.ts:242-289`. Same endpoint, same override flag. You were right that the backend is shared, and it exonerates the backend.

---

## The verified comparison

| Layer | AI Playlist | JoVE Labs | Verified in |
|---|---|---|---|
| Input | typed topic, plus page/article context | researcher's publications → extracted techniques | Playlist: Start node `startState`; Labs: `curriculum-generator.service.ts:280-291` |
| Query expansion | **1 topic → 10–20 LLM subtopics → 20 queries** | **1 method → 1 query. No expansion step exists.** | Playlist: node 18 `Analyzing your Topic...` + `buildSearchQueries()`; Labs: `module-video-matcher.service.ts:246-276` |
| Candidate pool | 100–480 rows (10×10 initial, up to 20×24) | ≤20 rows per method (2 category queries × `per_page` 10) | Playlist: `MAX_SEARCH_QUERIES=20`, `MAX_SEARCH_RESULTS_PER_KEYWORD=24`; Labs: `METHOD_CANDIDATES_PER_CATEGORY = 10` |
| Normalisation, unconditional? | **Yes** — every catalog search routes through the keyword LLM | **No** — the qualified search term is dropped on every human-touched path | Playlist edges: `conditionAgentAgentflow_0 → llmAgentflow_1 → customFunctionAgentflow_1`; Labs: `modules.service.ts:1376`, `labs.service.ts:801` |
| Disambiguation | **Yes** — 10 clarification kinds, deterministic guards, low-confidence re-ask | **None** | Playlist: node 02 prompt + `Validating action readiness...` `requireClarification()`; Labs: no equivalent found |
| Research corpus | gated on user role | always in scope, and it fills half the module | Playlist: `getCategoryFilter()` / `RESEARCH_ROLE_LABELS`; Labs: `lab-module-video.entity.ts:46-58` |
| Subscription filter at search | yes — Bearer token sent, `!isSubscribed` dropped | no auth header sent, no filter at search time | Playlist node 04; Labs `jove-api.service.ts:249-271` |
| Payload per candidate | `{id, t, ty}` | `{id, title, articleType}` | `compactCandidate()` / `curriculum-generator.service.ts:389` |
| Curation LLM | yes, one call over the whole merged pool | yes, one call over per-method pools | node 06 / `curriculum-generator.service.ts:421-430` |
| Hallucinated-id guard | yes, `requireCandidateMembership: true` | yes, `candidateById.get(id)` | `Building curated response...` L802, L812; `curriculum-generator.service.ts:454-455` |
| Shortfall behaviour | reports honestly: "I found N of M requested" | **catches its own honest failure and retries on a weaker path** | `Building curated response...` L1145; `curriculum-generator.service.ts:319-328` |
| Feedback loop | none wired | none wired (but latent signal exists) | flow `analytic: null`, no analytics nodes; `lab-module-video.entity.ts` |

---

## Finding 1 — Labs never expands the query. This is the main event.

The playlist treats "one topic" as "a family of searches". Node 18 (`Analyzing your Topic...`) is an LLM step that runs on **every** catalog search, and it produces up to 10 subtopics for a fresh playlist or 20 for an existing one, each capped at 5 words, ordered foundational → advanced, explicitly de-duplicated and de-generic'd. Then `buildSearchQueries()` in node 04 adds truncated 2-word variants of each for recall, and fires all of them in parallel:

```js
for (const item of base) {
  const words = normalizeRawInput(item).split(/\s+/).filter(Boolean);
  if (words.length > 1) extras.push(words.join(" "));
  if (words.length > 2) extras.push(words.slice(0, 2).join(" "));
}
```

Up to 20 queries × 24 results, merged and deduped into one pool of several hundred, and the curator then picks the best 20 from it. Relevance is bought by **breadth then selection**.

Labs does the opposite. `searchMethodCandidates` takes one string and issues two queries with it — one filtered to Concept types, one to Experiment types — at 10 results each. There is no subtopic step anywhere in the service. I searched for one under every name I could think of (`searchTerms`, `techniqueSearchTerms`, `keywords`, `subtopics`, `expand`); the only thing that exists is the single qualified `searchTerm` produced at extraction, which is a *narrowing* device, not a broadening one.

The consequence is structural. When a method's one query is a poor lexical match for the catalog — and a phrase like `"Anaerobic Microbial Cell Culture (E. coli K-12)"` frequently will be — Labs has no second chance. It gets back whatever loosely matched, and because the curator may only choose from that method's own candidates, a thin or wrong pool becomes a thin or wrong module. The curator cannot rescue a bad pool; it can only decline, and declining triggers Finding 2.

**This is the step to copy, and it is the whole recommendation if you only do one thing.**

## Finding 2 — the good path silently falls back to the bad one

`curriculum-generator.service.ts:319-328`:

```ts
try {
  return await this.previewVideoFirstModules(techniques, researchArea);
} catch (error) {
  // Keep the existing name-first path as a safety net for transient
  // search/LLM failures while the new preview curator is rolled out.
  this.logger.warn(`previewModules: video-first curation failed; using legacy fallback: ...`);
```

`previewVideoFirstModules` is the good path: per-method `search_ai` candidates, one curator call, candidate-membership validation. The `catch` is unqualified, so it swallows an LLM timeout, malformed JSON, a search timeout — **and** the deliberate `BadRequestException(NO_VIDEOS_FOR_METHODS_MESSAGE)` thrown at line 403 when no candidates were found at all.

The fallback is materially worse. It groups modules from method *names* before seeing any video, then matches videos with `matchModuleVideos`, which does something the good path never does: it **concatenates the module name and every method search term into a single query string** and searches once per category.

```ts
buildQuery(queryText: string, searchTerms?: string[]): string {
  const terms = (searchTerms ?? []).map((t) => String(t ?? '').trim()).filter((t) => t.length > 0);
  return [String(queryText ?? '').trim(), ...terms].filter((s) => s.length > 0).join(' ');
}
```

A term-salad query against a relevance-ranked backend returns documents matching the centroid of several unrelated concepts. That is a textbook off-topic generator.

Two things follow. First, an honest "we found nothing for these methods" is converted into a plausible-looking lab built the weak way — the architectural equivalent of padding. Second, **a user cannot tell which path built their lab, and neither can you**, because the only trace is a `logger.warn`. If your complaints are intermittent and you have not been able to reproduce them, this is almost certainly why.

## Finding 3 — the qualified search term is dropped on every path a human touches

The extraction prompt (`prompt-keys.ts:74-124`) does real work to produce two names per technique: a short display `name`, and a `searchTerm` "anchored to the organism, cell type, specimen, substrate, dataset, model family, or experimental condition from the paper". `"Cell Culture"` becomes `"Anaerobic Microbial Cell Culture (E. coli K-12)"`.

That qualification survives only on the initial generate-from-publications path. Everywhere a human is involved, it is discarded and replaced with the bare display name:

- `modules.service.ts:1376` — trainer edits a module's methods:
  ```ts
  techniques: methodSearchTerms.map((name) => ({ name, searchTerm: name })),
  ```
  The endpoint's signature is `refreshModuleVideos(labId, moduleId, techniques: string[], ...)`. A qualified term cannot reach it even in principle.
- `labs.service.ts:801` — manual single-module creation: same `{ name, searchTerm: name }`.
- Every DTO coerces a plain string to `{ name: v, searchTerm: v }` (`preview-lab-modules.dto.ts:23`, `check-module-videos.dto.ts:22`, `generate-lab.dto.ts:109`, `generate-lab-module.dto.ts:55`).

And it is not just for that request. `modules.service.ts:1459` writes the bare names back over the stored column:

```ts
techniqueSearchTerms: normalizeModuleTechniqueSearchTerms(methodSearchTerms),
```

So **one method edit permanently downgrades that module's search terms.** Every future re-match uses the generic names.

This matters for who is complaining. The path that demos well is the untouched AI-generated one. The people who complain are the ones who edited something — which is exactly the population whose feedback reaches customer success.

The playlist has the same hazard and closes it: normalisation is a graph node on the shared route, so the manual path, the edit path and the retry path all pass through it. There is no way to route around it.

## Finding 4 — Labs puts research articles in teaching modules, unconditionally

Playlist, node 04:

```js
const BASE_CATEGORY_FILTER = ["business", "jove_core", "science_education", "lab_manual"];
const RESEARCH_CATEGORY_FILTER = ["journal", "encyclopedia_of_experiments"];
```

`journal` and `encyclopedia_of_experiments` are added **only** when the user's role is in `RESEARCH_ROLE_LABELS` (postdoc, researcher, scientist, lab technician, and so on). A professor building teaching material never sees them.

Labs, `lab-module-video.entity.ts:46-58`:

```ts
[LabModuleVideoCategory.CONCEPT]:    ['jove_core', 'lab_manual_procedure'],
[LabModuleVideoCategory.EXPERIMENT]: ['journal', 'encyclopedia_of_experiments', 'science_education'],
```

Both buckets are always searched, and the render order is Concept-then-Experiment, so roughly half of every module is drawn from the research corpus by construction. A `journal` row is a specific published experiment, not a lesson on a method. To a trainee who asked to learn PCR and got a paper about one lab's PCR-based assay of a protein they have never heard of, that reads as off-topic — even though search did its job and the curator picked the best of what it was given.

I would treat this as the most likely single cause of complaints that are about *tone* rather than *topic* — "this isn't wrong exactly, it just isn't training material".

## Finding 5 — orphan methods get stapled onto the first module

`curriculum-generator.service.ts:1013-1033`:

```ts
const [first, ...rest] = modules;
return [
  { ...first, techniques: [...first.techniques, ...leftovers] },
  ...rest,
];
```

The curator is told "Leave a method out of modules if none of its candidates are relevant." `ensureInputTechniquesCovered` then takes every method the curator deliberately dropped and appends it to module 1. The module now advertises a method none of its videos teach. The videos may be individually fine; the module is still wrong, and it is wrong in a way a user will describe as "the videos don't match".

This runs on the legacy fallback path, which raises its importance given Finding 2.

## Finding 6 — nothing in Labs ever asks

The playlist devotes roughly a third of its graph to not guessing. Node 02 defines ten clarification kinds (`topic_domain`, `playlist_scope`, `save_target`, `count_meaning`, `edit_target`, `content_shortfall`, `conflicting_instructions`, and so on) with a rule that is worth reading literally:

> "Ask when it is genuinely polysemous or referentially unclear... Example: 'Create playlist on cell' without useful domain context is ambiguous between biological cells and electrochemical cells."

Then `Validating action readiness...` re-imposes it in code rather than trusting the model — `requireClarification()` is called from seven deterministic guards, and a separate resolver node forces a re-ask when a destructive action is answered with low confidence:

```js
if (isDestructive && confidence !== 'high') return { status: 'reask', matchedBy: 'resolver_low_confidence' };
```

Labs is unattended, so it cannot literally ask the researcher mid-run. But the mechanism transfers: the flow's real trick is that **ambiguity is a first-class outcome, not an error**. Labs already has a "Confirm Modules" review step, which is the natural place to surface "we were not confident about these two methods" instead of quietly producing a module anyway.

---

## What Labs already has and throws away

Worth stating, because the natural assumption is that Labs is behind at every layer and it is not.

**Labs retrieves `description` and `relevanceScore` for every candidate and discards both before the curator sees them.** `MatchedModuleVideo` (`module-video-matcher.service.ts:19-29`) carries `description` and `relevanceScore`; the payload built at line 389 keeps only `id`, `title`, `articleType`. The playlist never had descriptions to discard — the search response it parses does not carry them into `normalizeVideo()`.

So Labs can be given a strictly richer curation payload than the playlist has, at the cost of a two-field change to one `.map()`, with no new API calls and no new latency. That is the cheapest available quality lever in the codebase.

Labs' input is also richer in kind: a researcher's actual publications versus a typed topic. That context reaches technique extraction and then stops — the research area is passed to the curator as a string, but nothing about the papers informs retrieval. If the richer-input system produces worse output, the problem is not a missing recipe; it is that the extra context is being discarded before it can help. It is discarded at the query-expansion layer that does not exist.

---

## What to copy, in order

**1. Add a query-expansion step before search.** (Finding 1. Biggest effect.)
One LLM call per method, or one per lab covering all methods, producing 5–10 sibling subtopic queries per method, each ≤5 words, ordered foundational → advanced. Fire them in parallel, merge and dedupe by video id, hand the whole pool to the existing curator. Copy the *step*, not the playlist's prompt text — but node 18's constraint list is a good starting point, particularly the bans on near-duplicate keywords and on generic expansions like "overview" or "basics" that waste a query slot. Keep the qualified `searchTerm` as one of the queries; the point is to stop it being the *only* one.

**2. Make the fallback loud, or delete it.** (Finding 2. Cheapest, and it is a bug.)
At minimum: catch only transient errors, let `NO_VIDEOS_FOR_METHODS_MESSAGE` propagate so an honest empty result stays honest, and persist which path produced each lab. Do this before anything else, because until it is done you cannot tell whether any other fix worked.

**3. Stop discarding the qualified search term on the human-touched paths.** (Finding 3.)
Widen `refreshModuleVideos` to accept `{name, searchTerm}` like the other DTOs already do, and stop overwriting `techniqueSearchTerms` with bare names at `modules.service.ts:1459`. If a trainer edits methods, re-qualify the new ones rather than degrading the old ones. The general lesson from the playlist is that normalisation must sit on the shared path so no caller can route around it.

**4. Gate the research corpus.** (Finding 4.)
Copy `getCategoryFilter()`'s shape: teaching categories by default, `journal` and `encyclopedia_of_experiments` added only when the lab's audience justifies it. The playlist keys this off user role; Labs could key it off lab type or a trainer toggle. Note that Labs' Concept/Experiment split is a UI contract, so this needs a product decision about what fills the Experiment tab for a teaching-oriented lab — that is a question for the Labs PM, not a code change.

**5. Pass `description` and `relevanceScore` into the curator payload.** (Two lines. Do it while you are in the file.)

**6. Drop `ensureInputTechniquesCovered`, or make it visible.** (Finding 5.)
If the curator says a method has no relevant videos, that belongs in `unmappedTechniques` and on the warning card, not stapled to module 1.

**7. Surface low confidence at the Confirm Modules step.** (Finding 6. Product work, not a port.)

---

## The part you cannot copy as code

The playlist has no analytics wired — `analytic: null` on the flow, no Mixpanel or event nodes anywhere in the graph. What it has instead is a `_debug` envelope attached to every custom function return, carrying per-query `api_requests` with status, result counts, timings and the exact request body. Someone built that deliberately so they could open a run and see which of the 20 queries returned nothing. The playlist is good because a human iterated against that visibility, repeatedly. That is not an artifact you can port.

Labs has the same latency logging but not the same loop. It does, however, already sit on the signal it needs and is not using it: `lab_module_videos` has `relevance_score` and a `deleted_at` soft-delete column. **A soft-deleted row is a trainer telling you a suggested video was wrong.** You can compute removal rate sliced by `article_type`, by relevance score band, and by method — today, retroactively, with a query and no new instrumentation.

The one column worth adding is which generation path produced the row (video-first curated vs legacy fallback), because without it Finding 2 makes every other measurement ambiguous.

I would treat that query as a precondition rather than a follow-up. Right now "Labs suggests off-topic videos" is a report from customer success with no denominator. After it, you will know whether the complaints concentrate in `journal` rows (Finding 4), in edited modules (Finding 3), or in labs built on the fallback path (Finding 2) — and those three point at different fixes with very different costs.

---

## What still needs a human

Everything above is read off the graph and the source. Four things are not in either, and the graph will never tell you:

1. **Why the research corpus is unconditional in Labs.** It may be a deliberate product call — Labs is aimed at researchers, and the playlist's own role gate would *include* journal content for exactly the population Labs serves. If so, Finding 4 is not a bug and the fix is presentational rather than a filter change. Ask the Labs PM before touching it.
2. **Whether the legacy fallback is still needed.** The comment says "while the new preview curator is rolled out". If the rollout finished, the safety net is now the main source of bad output. Ask whoever wrote it what it was protecting against.
3. **Whether qualified search terms were ever measured to beat bare names.** The prompt invests heavily in them, but a long qualified noun phrase can retrieve *worse* than a short canonical one against a lexical backend. This is worth an A/B before you spend effort preserving them through the edit path — it is possible that Finding 3 is protecting something that does not help.
4. **What customer success actually means by "off-topic".** Wrong subject, right subject but research-not-teaching, or right videos under a module label that claims a method they do not cover. Those are Findings 1, 4 and 5 respectively, and they have different fixes. The removal-rate query above will separate them faster than more anecdotes will.

---

## Sources

- **AI Playlist**, agentflow `fe20a92c-9245-484b-88a9-155cbb1889cc` on `https://flowiseai.dev.test.jove.com`, 28 nodes. Nodes cited by their canvas labels: `Start`, `Planning request & clarifications...` (02), `Validating action readiness...` (03), `Searching JoVE library...` (04), `Organizing playlist...` (06), `Building curated response...` (07), `Analyzing your Topic...` (18), `Resolving your answer...` (27). Read via the graph, not via anyone's description of it.
- **JoVE Labs**, `~/dev/jove-code/research-svc` — chiefly `src/labs/services/ai/curriculum-generator.service.ts`, `src/labs/services/ai/module-video-matcher.service.ts`, `src/labs/services/ai/prompt-keys.ts`, `src/labs/services/modules.service.ts`, `src/labs/services/labs.service.ts`, `src/labs/entities/lab-module-video.entity.ts`, `src/campaigns/services/jove-api.service.ts`.
- Note there is a second, divergent checkout at `~/dev/jove-code/_research-svc-preview`. Every Labs citation above is from `research-svc`, the newer one. If anyone reviews these findings against the preview copy they will see different line numbers and, in places, different code.
