# AI Playlist — what the model sees when it picks videos, and what state the flow carries

**Source:** live read of the Flowise instance at `FLOWISE_API_ENDPOINT`, agentflow **"AI Playlist"**, id `bd799a71-9b90-4bdd-888e-627e3428fa55`, last updated 2026-08-17T08:16:30Z. Read-only (`GET /api/v1/chatflows`). Flow is `deployed: false`, `isPublic: false`.

---

## The short answer

Video selection happens in exactly **one** node: the LLM node labelled **"Organizing playlist..."** (`llmAgentflow_2`, model `gpt-5.6-luna`).

For each candidate video, that model sees **three fields and nothing else**:

| Field | Meaning | Source |
|---|---|---|
| `id` | JoVE article id (number) | `video.articleId` |
| `t` | Video title (string) | `video.title` |
| `ty` | Article type (string, e.g. `jove_core`, `science_education`, `lab_manual_procedure`, `school`) | `video.articleType` |

That is the entire per-video view. It is enforced by one function in the search node (`customFunctionAgentflow_1`, line ~450):

```js
function compactCandidate(video) {
  return {
    id: Number(video && video.articleId),
    t: String((video && video.title) || ""),
    ty: (video && video.articleType) || null,
  };
}
```

**No abstract, no excerpt, no transcript, no duration, no publication date, no journal/section, no author, no keywords, no relevance score, no thumbnail, no subscription flag, no URL.** The model selects on title text and article type alone.

This is worth saying plainly in the meeting: **the search engine ranks, the model only re-titles and re-orders.** The relevance judgement is made by JoVE's own `search_ai` endpoint; the model's contribution is grouping, sequencing, and labelling a set it cannot inspect beyond the title string.

Two specific things get discarded on the way in:

- The search node fetches `headerImage` and `excerpt` for videos already in the draft (`draftArticlesAsVideos`), then throws both away at `compactCandidate`. The excerpt is retrieved and never used for the decision.
- `stripSubscriptionFlag()` removes `isSubscribed` before candidates leave the search node, so the model cannot prefer videos the user actually has access to.

---

## The exact instruction the model is given

**System message** (verbatim, HTML stripped):

> You are a Subject Matter Expert holding a PhD, assigned to create a playlist using www.jove.com videos for a university professor.
> Your task is to select, label, and sequence the strongest relevant teaching videos from curation_context.candidates.
> You will receive a JSON object named curation_context in the user message.
> Read curation_context.mode:
> - If mode is "new", create a new playlist from curation_context.candidates.
> - If mode is "append", curate only newly searched videos and do not rewrite, remove, reorder, rename, or regroup existing draft labels/videos. In append mode, if a newly selected video clearly belongs in an existing draft label from existing_labels, use that existing label title exactly. If the new topic is unrelated or does not clearly fit an existing label, create concise new labels for the new videos. Your output labels are merge instructions for the response builder: matching existing label titles will append videos there; new label titles will be added at the end. In append mode, avoid videos listed in existing_article_ids.
> - If mode is "recalibrate", rebuild the entire playlist to target_count videos as one coherent teaching sequence. Select the strongest target_count videos from candidates (select fewer only if fewer are available). Every id in must_keep_ids MUST appear in the output. You may add up to new_slots videos that are not in must_keep_ids. Organize the combined selected set into concise labels with the best teaching flow. Do not invent ids. All selected ids still come only from candidates.
>
> Critical selection rules:
> - For mode "new" or "append": requested_count is the maximum number of videos to select for this operation.
> - For mode "recalibrate": use target_count as the final playlist size to select.
> - If fewer relevant candidates are available than the target, select all relevant available candidates (while still obeying must_keep_ids in recalibrate mode).
> - Prefer the strongest teaching set; do not try to create a comprehensive playlist unless the requested count is large enough.
> - Include specialized, procedural, applied, advanced, and teaching-adjacent videos only when they strengthen the selected set.
> - Stop once you have selected the requested/target count or exhausted relevant non-duplicate candidates.
>
> Labeling rules:
> - Create concise, specific labels that are useful to learners.
> - Labels should reflect the actual videos in the group.
> - Use generic labels like "Fundamentals", "Methods", "Applications", "Related Topic", or "Advanced Topic" only when they are truly the clearest option.
> - Split labels when one group becomes too broad.
> - Avoid duplicate or near-duplicate labels.
> - Every selected video must appear in exactly one label.
>
> Video selection rules:
> - Select only videos from curation_context.candidates.
> - Prefer the strongest teaching sequence over raw relevance alone.
> - Prefer introductory videos before advanced videos when both are relevant.
> - Avoid duplicate or near-duplicate titles unless they clearly cover different content.
> - Use ty and t to choose the best representative video when titles overlap.
>
> Ordering rules:
> - Order labels according to the best teaching flow.
> - Order videos within each label from simplest to most advanced.
> - If two videos are similar in level, order the broader or more foundational one first.
>
> Output rules:
> - Return JSON only.
> - Do not invent videos or identifiers.
> - Copy selected compact candidate objects exactly from curation_context.candidates.
> - Preserve id, t, and ty exactly as provided.
> - Do not add headerImage, isSubscribed, metrics, isNew, or profile fields.
> - Return unlabeledVideos as an empty array unless a selected video truly does not fit any label.
>
> IMP: Return exactly this shape:
> ```
> { "title": string,
>   "labels": [ { "title": string, "videos": [compact candidate objects copied exactly from curation_context.candidates, each using id, t, and ty] } ],
>   "unlabeledVideos": [] }
> ```

**User message** is two lines — the whole payload arrives as one serialised blob:

```
curation_context:
{{ $flow.state.curation_context }}
```

Note the instruction "Use ty and t to choose the best representative video when titles overlap" — this is the flow acknowledging that title and type are the only discriminators available.

Memory is **off** on this node (`llmEnableMemory: false`), so each curation call is stateless apart from `curation_context`.

**Structured output** is enforced with three keys: `title` (string), `labels` (jsonArray of `{title, videos[{id,t,ty}]}`), `unlabeledVideos` (jsonArray of `{id,t,ty}`).

---

## The full `curation_context` envelope

Around the candidate list, the model also sees the operating parameters. Built by `buildCurationContext()`:

**Modes `new` / `append`:**
`mode`, `topic`, `requested_count`, `available_count`, `subtopics[]`, `existing_labels[]`, `existing_article_ids[]`, `candidates[]`

**Mode `recalibrate`** adds: `target_count`, `direction` (`up`/`down`), `full_recreate`, `new_slots`, `must_keep_ids[]`

Mode is derived in code, not chosen by the model: `new` if the request scope is a new playlist, `append` if a draft already has videos, `recalibrate` when the user changes the playlist size.

### How many candidates reach the model

Candidates come from parallel POSTs to `{referrer}/api/free/search/search_ai` with `{query, page:1, per_page, category_filter, override_query:true}`. The queries are the topic plus the `search_keywords` produced by the upstream "Analyzing your Topic..." node (max 10 keywords with no draft, max 20 with one), each ≤5 words, ordered foundational to advanced.

Cap is `queries × per_page`, then deduped and truncated:

| Search mode | Max queries | Per page | Candidate ceiling |
|---|---|---|---|
| `initial_limited` (first playlist, no explicit count) | 10 | 10 | 100 |
| default / `detailed_full` / count changes | 20 | 24 | 480 |

`category_filter` is `["business","jove_core","science_education","lab_manual"]`, plus `["journal","encyclopedia_of_experiments"]` when the user's profile role is research-flavoured (postdoc, researcher, librarian, scientist, PhD student, lab manager, etc.) or `include_research_videos` is set.

Deduplication happens **before** the model, in code, by normalised title. Ties break on article type: `jove_core` (3) > `jove_education`/`science_education` (2) > everything else (1); then lower article id wins.

### What happens to the model's output

"Building curated response..." (`customFunctionAgentflow_2`) takes the ids back and **re-hydrates** the full video objects — `headerImage`, `excerpt`, `url`, `topic` — from `search_output.candidate_videos`, keyed by article id (`buildCandidateMap` / `hydrateVideo`). So the rich metadata exists in the flow throughout; it is deliberately withheld from the model and re-attached afterwards.

### Editing does not select videos

The other LLM node people assume is a selector, **"Curating edit operations..."** (`llmAgentflow_5`), explicitly cannot: *"Do not search for or add new catalog videos in this branch."* Its operations are restricted to `rename_playlist`, `add_label`, `rename_label`, `remove_label`, `remove_videos`, `move_video`, `reorder_labels`, `reorder_videos`. Size changes are bounced back to the recalibrate/search branch (it returns `{}`). Likewise "Enriching selected playlist..." (`llmAgentflow_6`) only names a topic/title/labels for a manual UI selection — *"Do not invent videos. Do not change video order or counts."*

**One model call decides the playlist contents, and it sees three fields per video.**

---

## State carried between steps

The Start node declares **37 keys** with `startPersistState: true`, so state survives across turns of a conversation. `startState` is exposed in `apiConfig.overrideConfig`, so the calling web app injects values per request.

### Injected by the caller — never written by any node

| Key | Notes |
|---|---|
| `user_access_token` | Read by 9 nodes; used as the Bearer token for search and save calls |
| `referrer` | Defaults to `https://www.jove.com/`; base URL for all API calls and video URLs |
| `ui_draft_playlist` | The live draft as the UI has it; entry point for UI-sync |
| `include_research_videos` | Overrides the role-based research-category decision |
| `page_context`, `page_info`, `current_article_id`, `current_article_content` | Page the user is on, for the on-page copilot entry |
| `clarification_response` | User's reply to a clarifying question |

### Written and consumed inside the flow

| Key | Written by | Purpose |
|---|---|---|
| `user_profile` | Fetching user profile | Role labels drive the research-category filter |
| `validated_plan` | Validating action readiness | The canonical parsed request; read by 9 nodes |
| `validated_route` | Validating action readiness | Router key: `TOPIC_SEARCH`, `EDIT_OR_COUNT`, `SAVE_PLAYLIST`, `EMBED_CODE` |
| `search_keywords` | Analyzing your Topic / Enriching selected playlist | Subtopic queries fanned out to search |
| `topics`, `available_count`, `pending_topic` | Searching JoVE library + response builders | Topic and candidate counts |
| **`curation_context`** | Searching JoVE library | **The whole curation payload, JSON-stringified — the single input to the selection model** |
| `draft_playlist` | 8 nodes, read by 16 | The working playlist; the most trafficked key in the flow |
| `draft_binding` | builders, validator, normalizer | Ties the draft to a saved playlist record |
| `saved_playlist`, `saved_playlists` | builders / Normalizing saved playlist | Persisted result(s) |
| `phase` | 5 builders | Conversation phase, starts at `greeting` |
| `pending_action` | validator, builders, normalizer | Action awaiting a user answer |
| `manual_selection_draft`, `bootstrap_mode` | Validating & detecting input, bootstrap title | Videos hand-picked in the UI |
| `turn_status`, `turn_resolution`, `resolver_context`, `resolver_status`, `resolver_option_id`, `resolver_value`, `resolver_confidence` | Resolving pending answer / Resolving your answer | Clarification-question resolution loop |

### Write-only — set but never read by any node

`last_intent`, `requested_count`, `selected_lms`, `share_action`. These are populated for the client to read off the returned state, not used for internal branching.

### Three things worth flagging before the meeting

1. **`curation_context` is not declared in the Start node's state.** It is the largest and most important payload in the flow, and it is created at runtime by the search node's state update rather than declared alongside the other 37 keys. It works (Flowise merges new keys on update), but it is invisible to anyone reading the Start node to learn the flow's state contract, and it is not covered by `overrideConfig`.
2. **`current_video_transcript` and `user_access_decision` are dead.** Declared in state, read by nothing, written by nothing. `current_video_transcript` in particular suggests transcript-aware curation was intended and never wired up — which is exactly the gap that leaves the selection model working from titles only.
3. **The model cannot see access.** `isSubscribed` is stripped before candidates are built, so nothing in the selection step prefers videos the professor can actually play.

---

## Node map (for reference)

```
Start
 └─ Fetching user profile ──> Checking your access
      ├─ (0) User not logged in
      └─ (1) Validating & detecting input ──> Route after UI validate
            ├─ (0) Enriching selected playlist ─> Setting bootstrap playlist title ─┐
            └─ (1) ─────────────────────────────────────────────────────────────────┤
                                                          Resolving pending answer <┘
                                                                    │
                                                          Route pending answer
                                                            ├─(0) Planning request & clarifications
                                                            ├─(1) Resolving your answer ─> Planning request…
                                                            └─(2) Validating action readiness
                                                                    │
                                              Planning request… ─> Validating action readiness
                                                                    │
                                                        Routing validated action  (on validated_route)
   ┌────────────────────────────────────────────────────────────────┼───────────────────────────────┐
   │ (0) TOPIC_SEARCH          │ (1) EDIT_OR_COUNT   │ (2) SAVE_PLAYLIST   │ (3) EMBED_CODE  │ (4) other
   │ Analyzing your Topic      │ Curating edit ops   │ Verifying playlist  │ Creating embed  │ Building
   │   ↓                       │   ↓                 │  ├─0,1 shortfalls   │   link          │ direct
   │ Searching JoVE library    │ Building edit resp. │  └─2 Saving ─>      │                 │ response
   │   ↓                       │                     │    Normalizing      │                 │
   │ ORGANIZING PLAYLIST  ← the only video-selection model call             │                 │
   │   ↓                       │                     │                     │                 │
   │ Building curated response │                     │                     │                 │
```

All five LLM nodes run `gpt-5.6-luna` via a custom OpenAI-compatible endpoint (`chatOpenAICustom`).
