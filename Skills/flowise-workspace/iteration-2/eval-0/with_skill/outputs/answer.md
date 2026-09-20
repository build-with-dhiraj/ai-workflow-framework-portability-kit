# AI Playlist — what the curation model sees, what it's told, and what state the flow carries

**Flow:** `AI Playlist` · type `AGENTFLOW` (Agentflow V2) · id `bd799a71-9b90-4bdd-888e-627e3428fa55`
**28 nodes, 29 edges** · instance `flowiseai.jove.com` · flow `updatedDate` **2026-08-17T08:16:30Z**
**Read from the live graph on 2026-08-17.** Read-only; no prediction endpoint was called.

There is exactly one flow named "AI Playlist" on this instance (18 flows total), so there is no
dev/prod ambiguity here — unlike AI Worksheet, AI Lesson Planner and slides, which all have
dev/PROD pairs. Every flow on the instance reports `deployed=false`, so that field is not being
used as a production marker; don't read it as "this flow isn't live."

---

## The short answer

1. **Per video, the model sees three fields and nothing else: the numeric article id, the title
   string, and the article type.** No abstract, no excerpt, no transcript, no keywords, no
   duration, no thumbnail, no author or journal, no date, no metrics.
2. **It is told to pick "the strongest relevant teaching videos", order them "simplest to most
   advanced", and avoid titles that "clearly cover different content."** Those are pedagogical-level
   and content-overlap judgments. A title and a type cannot support them. This is a payload problem,
   not a prompt problem — no amount of prompt tuning fixes it.
3. **State is 37 keys declared on the Start node, persisted across turns** (`startPersistState: true`).
   `draft_playlist` is the spine — 16 of 28 nodes touch it. One key, `curation_context`, is written
   but never declared, and it happens to be the exact channel that feeds the curation model.

---

## Which node makes the decision

The playlist-building path is four nodes:

```
Analyzing your Topic...      llmAgentflow_1              → produces search_keywords
Searching JoVE library...    customFunctionAgentflow_1   → BUILDS THE PAYLOAD
Organizing playlist...       llmAgentflow_2              → MAKES THE SELECTION
Building curated response... customFunctionAgentflow_2   → validates and assembles the draft
```

The selection is made by **"Organizing playlist..."** (`llmAgentflow_2`), an LLM node running
`gpt-5.6-luna` via `chatOpenAICustom`, with default temperature and no token cap set.

Its **entire user message is one line**:

```
curation_context: {{ $flow.state.curation_context }}
```

`llmEnableMemory` is `false` on this node. So no chat history, no user profile, no page context and
no article context reach it. Everything the model knows when it decides the playlist comes from that
single JSON object.

## What the model gets to see about each video

`curation_context` is built by **"Searching JoVE library..."** (`customFunctionAgentflow_1`) in
`buildCurationContext()`, and every candidate is passed through this function:

```js
function compactCandidate(video) {
  return {
    id: Number(video && video.articleId),
    t: String((video && video.title) || ""),
    ty: (video && video.articleType) || null,
  };
}
```

That is the whole per-video payload: **`id`, `t` (title), `ty` (article type)**.

The narrowing happens in two stages, and it is worth knowing that richer data exists upstream and is
deliberately dropped:

| Stage | Function | Fields kept |
|---|---|---|
| Search-result normalization | `normalizeVideo()` | `articleId`, `title`, `headerImage`, `articleType`, `topic`, `isSubscribed` |
| Compaction for the model | `compactCandidate()` | `id`, `t`, `ty` |

Two details that matter for the meeting:

- **`normalizeVideo()` already discards everything the JoVE search API returns beyond those six
  fields.** The node even has a `console.log("item", JSON.stringify(item))` on unsubscribed items, so
  the raw response is richer than what is retained.
- **`draftArticlesAsVideos()` — the function that turns existing draft videos into candidates — does
  carry an `excerpt` field.** `compactCandidate()` then throws it away. So a short description is
  already in reach inside this very node and never reaches the model.

The **context around** the candidate list (not per-video) is richer:

| Field | Present in | Meaning |
|---|---|---|
| `mode` | all | `"new"`, `"append"` or `"recalibrate"` |
| `topic` | all | the resolved topic string |
| `requested_count` | all | how many videos this operation asks for |
| `available_count` | all | how many candidates were found |
| `subtopics` | all | deduped subtopic strings |
| `existing_labels` | all | current draft's label titles, for merge-by-title |
| `existing_article_ids` | all | ids already in the draft, to avoid |
| `target_count`, `direction`, `full_recreate`, `new_slots`, `must_keep_ids` | recalibrate only | resize semantics |

## What instruction it is given

A single **system prompt of 3,925 characters**. It opens:

> "You are a Subject Matter Expert holding a PhD, assigned to create a playlist using www.jove.com
> videos for a university professor. Your task is to select, label, and sequence the strongest
> relevant teaching videos from curation_context.candidates."

It then sets out mode-specific behaviour (new / append / recalibrate), then five rule blocks —
critical selection, labeling, video selection, ordering, output — and closes with an exact required
JSON shape (`title`, `labels[].videos[]`, `unlabeledVideos`). The node also has a structured-output
schema enforcing that each returned video carries only `id`, `t`, `ty`, each described as "copied
exactly from curation_context.candidates".

### The mismatch to raise in the meeting

The prompt asks for judgments the three-field payload cannot support. Quoting the rules directly:

- "select, label, and sequence the **strongest relevant teaching** videos"
- "Prefer the **strongest teaching sequence** over raw relevance alone"
- "Prefer **introductory videos before advanced** videos when both are relevant"
- "Order videos within each label **from simplest to most advanced**"
- "If two videos are **similar in level**, order the **broader or more foundational** one first"
- "Avoid duplicate or near-duplicate titles unless they **clearly cover different content**"
- "Include specialized, procedural, applied, advanced, and teaching-adjacent videos **only when they
  strengthen the selected set**"

Every one of those is a claim about difficulty, pedagogical level, or content overlap. The only
evidence in the payload is a title string and a type enum. Difficulty is being inferred from title
wording; "clearly cover different content" is undecidable when two titles are near-identical and
nothing else is provided.

The prompt is, to its credit, explicit about the constraint it is operating under:

> "Use `ty` and `t` to choose the best representative video when titles overlap."

So the flow itself acknowledges the model is choosing on type and title alone. That is the finding:
**the ceiling on playlist quality here is set by the payload, not the prompt.** The cheapest
intervention is adding `excerpt` to `compactCandidate()` — it is already present on the draft path in
the same node.

One related note: a difficulty/quality signal already exists in code but is never shown to the model.
`getVideoPreferenceScore()` scores `jove_core`=3, `jove_education`/`science_education`=2, everything
else=1 — but it is used only as a de-duplication tie-break, not passed in the payload.

The `ty` vocabulary the model reasons over: `jove_core`, `science_education`, `jove_education`,
`lab_manual`, `lab_manual_procedure`, `school`, `business`.

## What is actually enforced vs. merely requested

Useful distinction if anyone asks "can the model go off-script":

**Enforced in code** (real constraints):
- *"Do not invent ids"* — "Building curated response..." calls `dedupeArticles()` with
  `requireCandidateMembership: true`, so any id not in the candidate map is dropped.
- *Counts* — `trimDraftToCount()` and `keepSet = ordered.slice(0, targetCount)` cap the final draft.
- *Label titles* — truncated to 50 chars; playlist title to 255.

**Advisory only** (no backstop):
- Every selection-quality and ordering rule above. If the model orders badly or picks weakly, nothing
  downstream notices or corrects it.

## What limits the candidate pool before the model sees it

- Candidate cap is `queries.length × per_page`. Default pass: up to `MAX_SEARCH_QUERIES = 20` queries
  × `MAX_SEARCH_RESULTS_PER_KEYWORD = 24`. Bootstrap/initial pass: `MAX_INITIAL_SEARCH_QUERIES = 10`
  × `DEFAULT_SEARCH_RESULTS_PER_KEYWORD = 10`.
- **Only subscribed videos survive collection** — the collector skips anything where `isSubscribed`
  is falsy, before de-duplication.
- Category filter is `business, jove_core, science_education, lab_manual`, widened with research
  categories **only** when the user's `roleLabel` or `otherRoleLabel` matches a research role
  (`shouldIncludeResearchVideos()`).
- De-duplication is by normalized title, keeping the higher-`getVideoPreferenceScore()` item and, on
  a tie, the lower article id.
- In `new`/`append` mode, candidates already in the draft are filtered out; in `recalibrate`, existing
  and searched candidates are merged and existing ids become `must_keep_ids`.

---

## The state the flow carries between steps

Agentflow V2 state must be declared on the Start node; operational nodes update declared keys via
their `updateState` map. Here the Start node declares **37 keys**, and `startPersistState` is
**`true`** — so state survives across turns of a chat session, not just one execution. That is what
makes the clarification loop (`pending_action` → user answers → reconstruct original command) work at
all.

| Group | Keys |
|---|---|
| **Playlist data (the spine)** | `draft_playlist`, `draft_binding`, `saved_playlist`, `saved_playlists`, `ui_draft_playlist`, `manual_selection_draft`, `bootstrap_mode` |
| **Conversation control** | `phase` (initialised `"greeting"`), `pending_action`, `turn_status`, `turn_resolution`, `clarification_response` |
| **Clarification resolver** | `resolver_context`, `resolver_status`, `resolver_option_id`, `resolver_value`, `resolver_confidence` |
| **Request plan** | `topics`, `pending_topic`, `search_keywords`, `requested_count`, `available_count`, `validated_plan`, `validated_route`, `last_intent` |
| **Identity / access** | `user_access_token`, `user_profile`, `user_access_decision`, `referrer` (default `https://www.jove.com/`) |
| **Page / article context** | `page_context`, `page_info`, `current_article_id`, `current_article_content`, `current_video_transcript` |
| **Misc** | `selected_lms`, `share_action`, `include_research_videos` |

**`draft_playlist` is the spine** — referenced by 16 of the 28 nodes. Anything that reads or writes
the playlist reads it. `manual_selection_draft` is deliberately kept separate from it: the planner
prompt states manual UI selections are "intentionally separate from current_draft" and must never be
merged or discarded implicitly.

**11 declared keys are never written by any node** — `user_access_token`, `user_access_decision`,
`referrer`, `ui_draft_playlist`, `page_context`, `page_info`, `current_article_id`,
`current_article_content`, `current_video_transcript`, `clarification_response`,
`include_research_videos`. These are inbound-only: the caller supplies them at invocation and the flow
only reads them. Worth knowing because `overrideConfig` is disabled by default per-property since
Flowise 2.1.4 (the flow's Security tab). If any of these ever look empty inside the flow, check that
tab before debugging the graph — I did not inspect the Security settings, so that is a place to look,
not a diagnosis.

### One anomaly worth flagging

**`curation_context` is written but never declared.** "Searching JoVE library..." writes four keys via
its `updateState` map:

```
topics            <- {{ output.topics }}              ← declared in Start
available_count   <- {{ output.candidate_count }}     ← declared in Start
pending_topic     <- {{ output.next_pending_topic }}  ← declared in Start
curation_context  <- {{ output.curation_context_json }}  ← NOT declared in Start
```

It is the **only** undeclared write in the entire flow — I checked every node's `updateState` map
against the Start declarations. In Agentflow V2 operational nodes are only meant to update keys the
Start node declared; they cannot create new ones. So this single binding is the one place in the flow
relying on undeclared-key behaviour, and it is precisely the channel carrying the candidate list into
`llmAgentflow_2`.

Stated honestly: I verified the declaration list and the write, and did not observe a failure. But if
that key ever resolves empty, "Organizing playlist..." receives the literal text `curation_context:`
followed by nothing, and curates from an empty candidate set — with no guard anywhere between the two
nodes to catch it. Adding `curation_context` to the Start node's state list is a one-line change that
removes the question entirely.

---

## How to re-verify any claim above

```bash
export FLOWISE_API_ENDPOINT=https://flowiseai.jove.com FLOWISE_API_KEY=<key>   # key not recorded here

node scripts/flowise.mjs nodes   "AI Playlist"                             # the 28-node map
node scripts/flowise.mjs vars    "AI Playlist"                             # the state contract
node scripts/flowise.mjs prompts "AI Playlist"                             # all 10 prompts, decoded
node scripts/flowise.mjs code    "AI Playlist" --node "Searching JoVE library"    # compactCandidate()
node scripts/flowise.mjs code    "AI Playlist" --node "Building curated response" # the enforcement
```

Flows are edited in a GUI with no version history a reader can consult, so the prompt and code quoted
here are what the graph said on **2026-08-17**. If this is being read later, re-run the commands
before quoting it.
