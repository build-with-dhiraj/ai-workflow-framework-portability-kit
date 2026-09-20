# Why the AI Playlist beats Labs on relevance, and what to copy

## The short answer

The playlist is not better at searching. It runs the same endpoint you do. It is better at **throwing things away**.

For one topic, the playlist retrieves somewhere between 100 and 480 candidate videos and then keeps about 20. Labs' main path retrieves 6 candidates per module and keeps up to 6. The playlist has a selection ratio of roughly 10:1; Labs' main path has a ratio of 1:1, which means it has no selection step at all — whatever the search returns *is* the module. Every quality decision the playlist makes happens in that gap, and Labs' main path does not have the gap.

Three things fill it, in order of how much they matter:

1. **One topic becomes up to 20 separate searches, not one long query.** Labs concatenates the module name and every method term into a single string and searches once.
2. **An LLM curator picks the final set from a large candidate pool, and code enforces that it can only pick real IDs.** Labs' main path has no curator.
3. **The corpus is narrowed before the search, by audience.** The playlist only lets journal and Encyclopedia of Experiments videos into the pool for research-role users. Labs pulls them into every module for everyone.

Item 3 is my leading suspect for the specific complaint you are hearing, and it is the cheapest to test. Items 1 and 2 are the real fix.

---

## What the playlist actually does

Read live from the `AI Playlist` agentflow (`fe20a92c-9245-484b-88a9-155cbb1889cc`) on the dev Flowise instance. Nodes named below are the labels you will see in the canvas.

### Step 1 — Expand the topic into teaching subtopics ("Analyzing your Topic...")

Before anything is searched, an LLM turns the single user topic into a list of subtopics. The prompt is strict about shape, and the shape is what makes the downstream search work:

- Max 10 subtopics when there is no existing draft, max 20 when there is.
- **Each subtopic is 5 words or fewer.**
- Ordered foundational to advanced, "teaching-friendly sequence".
- Must be distinct and non-overlapping; no near-duplicates or rewordings.
- Canonical academic terminology, lowercase unless required.
- Explicitly banned: "overview", "introduction", "basics", "of physics", and anything that just rephrases the parent topic.

The output is a structured `stringArray`, not free text.

### Step 2 — Fan out into many short parallel searches ("Searching JoVE library...")

The search node takes the topic plus those subtopics, dedupes them, and **adds truncated variants** — for any phrase over two words it also queries the first two words. That list is capped at 20 queries (10 in the lighter "initial" mode).

Every query is fired **in parallel** as its own POST to `/api/free/search/search_ai`:

```
{ query, page: 1, per_page, category_filter, override_query: true }
```

`per_page` is 10 in initial mode, 24 otherwise. So the candidate ceiling is `queries x per_page` — 100 in the light path, up to 480 in the full path — to fill a default 20-video playlist.

The important property: **each query is short and single-concept.** Nothing ever sends a long concatenated string to the search backend.

### Step 3 — Filter the pool in code, before any model sees it

Three filters, all in plain JavaScript:

- **Audience-scoped category filter.** The base filter is `["business", "jove_core", "science_education", "lab_manual"]`. The research categories `["journal", "encyclopedia_of_experiments"]` are appended **only** when the user's role matches a research role — postdoc, PhD student, researcher, scientist, lab technician, librarian, director, and similar. A professor building a teaching playlist never sees journal content unless they asked for it.
- **Subscription filter.** Any result where `isSubscribed` is false is dropped from the pool entirely. Candidates the user cannot play never become suggestions.
- **Duplicate collapse with a type preference.** Dedupe is by article ID *and* by normalized title. When two different IDs have the same normalized title, it keeps the pedagogically better one: `jove_core` scores 3, `science_education`/`jove_education` scores 2, everything else scores 1; ties break to the lower article ID.

### Step 4 — Compress candidates, then let a curator choose ("Organizing playlist...")

Each surviving candidate is compacted to three fields — `{ id, t, ty }` — id, title, article type. Nothing else. That is what makes it affordable to put hundreds of candidates in one prompt.

Those go into a single structured object, `curation_context`, with an explicit contract: `mode` (new / append / recalibrate), `topic`, `requested_count`, `target_count`, `available_count`, `subtopics`, `existing_labels`, `existing_article_ids`, `must_keep_ids`, `candidates`.

The curator prompt's rules that matter for relevance:

- Select **only** from `curation_context.candidates`. Do not invent IDs. Copy `id`, `t`, `ty` exactly.
- `requested_count` is a **maximum**, not a target. "If fewer relevant candidates are available than the target, select all relevant available candidates." It is explicitly allowed to return a short playlist rather than pad it.
- "Prefer the strongest teaching set; do not try to create a comprehensive playlist."
- Prefer introductory before advanced. Use `ty` to break ties when titles overlap.
- Every selected video must sit in exactly one label; labels must reflect their actual contents; split labels that get too broad.

Output is schema-constrained JSON: `{ title, labels: [{ title, videos: [{id, t, ty}] }], unlabeledVideos: [] }`.

### Step 5 — Enforce the contract in code ("Building curated response...")

This is the part people forget when they copy a curator prompt. The response builder rebuilds a map of the real candidates by article ID and re-hydrates each selected video from it. Every selection passes through `dedupeArticles(..., { requireCandidateMembership: true })`. **Any ID the model returned that is not in the candidate map is silently dropped.** The prompt asks the model not to hallucinate; the code guarantees it cannot.

### Step 6 — Ask one question instead of guessing ("Planning request & clarifications...")

Ahead of all of this sits a planner that can refuse to run. It returns a readiness of `ready`, `needs_clarification`, or `unsupported`, and when it clarifies it asks **exactly one** question from a fixed taxonomy — including `topic_domain` for genuinely polysemous terms. The prompt's own example: "create playlist on cell" is ambiguous between biological and electrochemical cells, so ask; "cell division" is already specific, so do not.

It is disciplined about this: "Do not ask merely because a topic is broad. Ask when it is genuinely polysemous or referentially unclear." The pending question is persisted, so the next turn is interpreted as an answer to it rather than as a new command.

---

## What to copy, in priority order

**1. Stop concatenating. One search per method, short.**
This is the highest-value change and probably the cheapest. `search_ai` is a vector path — a query string containing a module name plus five unrelated method names embeds to the centroid of all six concepts, which is close to none of them. That produces exactly the symptom your users report: results that are vaguely in the neighbourhood and specifically wrong. The playlist never exceeds a few words per query and pools the results afterward.

**2. Expand each method into 3-10 short sibling terms before searching.**
Same node, same prompt shape as "Analyzing your Topic...": ≤5 words, distinct, canonical terminology, no filler. For Labs the parent concept is a method rather than a topic, so the expansion should be technique variants, instrument or reagent qualifiers, and adjacent standard procedures. This is what turns a thin pool into a pool worth selecting from.

**3. Retrieve 5-10x what you will keep, then curate down.**
The number to move is the candidate-to-kept ratio. A curator choosing 3 videos from 6 candidates is a rubber stamp. Choosing 3 from 60 is curation.

**4. Compact candidates to `{id, title, articleType}` before prompting.**
This is the trick that makes step 3 affordable. Do not send descriptions or thumbnails to the curator.

**5. Give the curator permission to return fewer.**
The playlist prompt makes `requested_count` a ceiling and says so twice. If Labs asks for 3 videos per module and the model believes it must produce 3, it will pad with the least-bad option in the pool — and padding is what an off-topic complaint looks like from the inside. A short module is a better product than a padded one.

**6. Gate selections by ID membership in code, not just in the prompt.**
`requireCandidateMembership: true`. Cheap, and it converts a class of silent quality bugs into a dropped row.

**7. Scope the category filter by audience, not just by UI tab.**
The playlist's filter answers "what kind of content should this person see". Labs' filter answers "which tab does this go on". Those are different questions and Labs is only asking the second one.

---

## What to go and check on the Labs side

There are working snapshots of the Labs services in this workspace at `/private/tmp/claude-502/-Users-Dhiraj-dev/4c7ddfbe-e9e8-4924-be89-edd590fff829/scratchpad/` (`h_curriculum-generator.service.ts`, `h_modules.service.ts`, `h_jove-api.service.ts`, `head_src_labs_services_ai_module-video-matcher.service.ts`, `head_src_labs_entities_lab-module-video.entity.ts`). They were pulled earlier today by another session, so **treat everything in this section as a lead to confirm against the live branch, not as a verified finding.** The playlist half of this document is verified live from Flowise; this half is not.

Confirm these seven, roughly in this order:

**1. Is the concatenated query still live? (highest priority)**
In `module-video-matcher.service.ts`, `buildQuery(queryText, searchTerms)` does `[queryText, ...terms].join(' ')` — module name plus every method term in one string. That single string is what goes to search. Confirm this is still what the generation path uses, and check the actual query strings in your logs: `matchModuleVideos` logs `query="..."` truncated to 80 chars. If those log lines read like sentences rather than phrases, this is your bug.

**2. Is `per_page: 3` still the candidate cap?**
`VIDEOS_PER_CATEGORY = 3` is passed as `per_page` while `SEARCH_TOPK_PER_CATEGORY = 30` is passed as `topK`. Two categories at 3 each is a 6-video pool for a module that keeps up to 6. There is nothing for a curator to do. Note there is already a comment in that file about decoupling `topK` from `per_page` to fix a "max 3 total" symptom — so someone has been here before; check whether the fix went far enough.

**3. Which path actually runs in production — legacy or curator?**
There are two. `matchModuleVideos` is the legacy path: two searches, no LLM, keep everything. `previewVideoFirstModules` / `curateSingleModuleVideos` / `enrichModulesWithCuratedVideos` is a newer video-first curation path that already looks like the playlist — per-method `search_ai` calls, a compact candidate list, an LLM curator, and a `candidateById.get(id)` membership gate that drops hallucinated IDs. **But the new path is guarded by `typeof ... === 'function'` capability checks with a legacy fallback**, and there is a log line about falling back "while the new preview curator is rolled out". Find out which one served the labs your users complained about. It is entirely possible half the fix already shipped and is silently falling back.

**4. Is `EXPERIMENT` pulling journal content into every module?**
In `lab-module-video.entity.ts`, `VIDEO_CATEGORY_FILTERS[EXPERIMENT]` is `['journal', 'encyclopedia_of_experiments', 'science_education']`. Every Labs module unconditionally searches journal and Encyclopedia of Experiments — the exact two categories the playlist withholds from non-research users. Journal videos are single-lab research protocols; in a training module aimed at teaching a method, they read as off-topic even when the vector match is technically fine. Worth pulling five of the complained-about modules and checking how many of the bad suggestions have `articleType` of `journal`, `research`, or `encyclopedia_of_experiments`. That query answers the question in an afternoon.

**5. Does anything filter by subscription?**
I found no `isSubscribed` check anywhere in the Labs matcher or the JoVE API service — only an unrelated comment mentioning `lab-subscription-access.client.ts`. The playlist drops unsubscribed results before the pool is built. If Labs is suggesting videos the institution cannot play, that will be reported as "off-topic" by users who do not distinguish the two.

**6. Is `category_filter` ever omitted?**
Both Labs search helpers only include `category_filter` when the caller passes a non-empty list. Check the backend default for that case: in `SearchService.php`, `mapContentTypeToCategoryFilterForPython` falls through to `['journal', 'encyclopedia_of_experiments', 'jove_core', 'science_education', 'lab_manual_procedure', 'business']` — the entire corpus, journal included. Any Labs call path that omits the filter is searching everything.

**7. Is `relevanceScore` captured and then ignored?**
`LabModuleVideo` persists a `relevance_score` column and the matcher reads `score` / `relevanceScore` off each row, but I found no code that filters or sorts on it. Worth checking whether the scores on the complained-about videos are actually low — if they are, you have a free signal already in the database, and a floor is a one-line change while the curator work lands. If they are not low, that tells you the retrieval is fine and the problem is entirely selection, which sharpens everything above.

---

## What not to copy

**Do not copy the playlist's relevance threshold — there isn't one.** The playlist has no score cutoff anywhere. It gets its precision from fan-out plus curation, not from filtering on scores. If you add a threshold instead of a curator you will get shorter bad modules rather than good ones. (A threshold is still worth considering as an interim mitigation while the real fix lands, which is why it is check 7 above — but it is a stopgap, not the pattern.)

**Do not copy the clarification loop yet.** It is genuinely good, and it is the right long-term answer for ambiguous inputs. But Labs starts from a researcher's own published articles, which is a far less ambiguous starting point than a free-text topic box, and there is no conversational turn to ask into. Lower value per unit of work than items 1-3.

**Do not copy the append / recalibrate / must-keep machinery.** A large share of the playlist's complexity is edit-flow bookkeeping — growing, shrinking, and rebuilding an existing draft without disturbing what the user already curated. It is unrelated to first-generation relevance. Ignore it until Labs has an edit flow with the same requirements.

---

## Confidence

- **Verified live:** every claim about the playlist. Read directly from the `AI Playlist` agentflow on the dev Flowise instance, including node prompts, the search function body, the constants, and the response builder's membership gate.
- **Corroborated:** the search backend's behaviour for `override_query` and the `category_filter` default. Read from the `SearchService.php` / `SearchController.php` snapshots in this workspace, and consistent with the endpoint the playlist calls.
- **Unverified, needs your confirmation:** every claim in the "go and check" section. Those come from local snapshots of Labs services pulled by an earlier session, not from a live read of the branch. The file and symbol names should be accurate enough to navigate by; the conclusion that any given path is *live in production* is exactly what I could not establish and what item 3 asks you to settle first.
