# AI Playlist — what the curation model actually sees, and what state the flow carries

Read live from `https://flowiseai.dev.test.jove.com`, agentflow **AI Playlist**, id `fe20a92c-9245-484b-88a9-155cbb1889cc`, last updated **14 Aug 2026**. (There is a second flow named "AI Playlist dev", id `6e4cfab8-...` — everything below is from the non-dev one.)

## The short answer

Video selection happens in exactly **one** node: the LLM step labelled **"Organizing playlist..."** (`llmAgentflow_2`), running `gpt-5.6-luna` through a custom OpenAI-compatible endpoint, with **chat memory turned off**.

For each candidate video that model sees **three fields and nothing else**:

| Field | Meaning |
|---|---|
| `id` | JoVE article id (number) |
| `t` | Video title (string) |
| `ty` | Article type (e.g. `jove_core`, `school`, `lab_manual_procedure`) |

That is the entire per-video representation. It is produced by `compactCandidate()` in the "Searching JoVE library..." node.

**What the model does NOT see about each video:** abstract or excerpt, description, transcript, duration, publication date, authors, journal/section, thumbnail, view counts or any engagement metric, subscription status, relevance score, search rank, or which of the ~20 search queries surfaced it. The search step actually *fetches* the thumbnail (and pulls `excerpt` for videos already in the draft), then discards those fields before building the model's payload. Subscription status is stripped deliberately (`stripSubscriptionFlag`), and the prompt explicitly forbids the model from adding `headerImage`, `isSubscribed`, `metrics`, `isNew`, or profile fields back into its output.

So when the prompt tells it to "use `ty` and `t` to choose the best representative video when titles overlap" — that is literal. Title and article type are the only discriminators it has. Ordering of the candidate list (search-result order, deduped) is the only implicit extra signal.

## The full payload: `curation_context`

The model gets one user message containing a single JSON object, `curation_context`:

| Key | Contents |
|---|---|
| `mode` | `"new"`, `"append"`, or `"recalibrate"` |
| `topic` | The resolved topic string |
| `requested_count` | Max videos to select this operation |
| `available_count` | How many candidates were found |
| `subtopics` | The generated search keywords |
| `existing_labels` | Label titles already in the user's draft |
| `existing_article_ids` | Article ids already in the draft (to avoid re-adding) |
| `candidates` | The compact `{id, t, ty}` list |
| `target_count`, `direction`, `full_recreate`, `new_slots`, `must_keep_ids` | Recalibrate mode only |

Because memory is disabled on this node, the system prompt plus this object is the model's *complete* world. No conversation history, no user profile, no page context.

## The instruction it is given

Persona and task, verbatim from the system prompt:

> "You are a Subject Matter Expert holding a PhD, assigned to create a playlist using www.jove.com videos for a university professor."
> "Your task is to select, label, and sequence the strongest relevant teaching videos from curation_context.candidates."

**Mode branches**
- `new` — build a fresh playlist from the candidates.
- `append` — curate only the newly searched videos; do not rewrite, remove, reorder, rename, or regroup existing labels. If a new video fits an existing label from `existing_labels`, reuse that title *exactly* (the response builder treats matching titles as merge instructions); otherwise create new labels appended at the end. Avoid ids in `existing_article_ids`.
- `recalibrate` — rebuild the whole playlist to `target_count` as one coherent sequence. Every id in `must_keep_ids` **must** appear. It may add at most `new_slots` videos beyond those.

**Selection rules**
- `requested_count` is the maximum for new/append; `target_count` is the final size for recalibrate.
- If fewer relevant candidates exist than the target, take all relevant ones (still honouring `must_keep_ids`).
- "Prefer the strongest teaching set; do not try to create a comprehensive playlist unless the requested count is large enough."
- Include specialised/procedural/applied/advanced videos only when they strengthen the set.
- Stop at the requested count or when relevant non-duplicate candidates are exhausted.
- Select only from `candidates`. Do not invent ids.

**Labeling rules** — concise, specific, learner-useful labels reflecting the actual videos; generic labels ("Fundamentals", "Methods", "Applications", "Related Topic", "Advanced Topic") only when genuinely clearest; split labels that get too broad; no duplicate or near-duplicate labels; every selected video in exactly one label.

**Ordering rules** — order labels by best teaching flow; within a label, simplest to most advanced; when two are at a similar level, the broader/more foundational one first. Prefer introductory before advanced. Avoid duplicate or near-duplicate titles unless they clearly cover different content.

**Output rules** — JSON only, this exact shape, with `id`/`t`/`ty` copied verbatim from the candidates:

```json
{
  "title": "string",
  "labels": [ { "title": "string", "videos": [ { "id": 0, "t": "", "ty": "" } ] } ],
  "unlabeledVideos": []
}
```

`unlabeledVideos` should be empty unless a selected video truly fits no label. The shape is enforced as a structured-output schema on the node, not just requested in prose.

## Where the candidates come from (one level up)

1. **"Analyzing your Topic..."** (`llmAgentflow_1`, same model, memory off) turns the topic into subtopic keywords — max 10 when there is no existing draft, max 20 when there is; max 5 words each; ordered foundational → advanced; canonical academic terminology.
2. **"Searching JoVE library..."** (`customFunctionAgentflow_1`) expands topic + keywords into up to **20 queries** (capped at **10** on the first pass), fires them **in parallel** at `POST {referrer}/api/free/search/search_ai` with `per_page: 24` and `override_query: true`.
3. `category_filter` defaults to `business`, `jove_core`, `science_education`, `lab_manual`; `journal` and `encyclopedia_of_experiments` are added when research videos are enabled (via the `include_research_videos` flag or a research-type role on the user's profile).
4. Results are deduped by article id and by a title key. **Anything the user is not subscribed to is dropped before curation** — the model never sees unsubscribed content.
5. Everything then collapses to `{id, t, ty}`.

## After the model picks

**"Building curated response..."** (`customFunctionAgentflow_2`) rehydrates each `{id, t, ty}` back into a full video object (thumbnail, article type, topic) by looking the id up in the search node's full candidate map. Any id not in that map is dropped — a hard hallucination guard. Then "Verifying playlist" checks the access token and draft are non-empty before "Saving the playlist" and "Creating embed link...".

Worth knowing for the meeting: the **edit** branch ("Curating edit operations...", `llmAgentflow_5`) is explicitly barred from touching video selection — "Do not search for or add new catalog videos in this branch." It only does `rename_playlist`, `add_label`, `rename_label`, `remove_label`, `remove_videos`, `move_video`, `reorder_labels`, `reorder_videos`. So *all* video selection in this product goes through the single node above.

## The state the flow carries

The Start node declares **37 state keys** with `startPersistState: true`, so they persist across turns within a chat session.

| Group | Keys |
|---|---|
| Identity & access | `user_access_token`, `user_profile`, `user_access_decision`, `referrer` (defaults to `https://www.jove.com/`) |
| Conversation phase | `phase` (initial value `"greeting"`), `last_intent`, `turn_status`, `turn_resolution` |
| Topic & search | `topics`, `pending_topic`, `search_keywords`, `include_research_videos` |
| Counts | `requested_count`, `available_count` |
| Playlist artifacts | `draft_playlist`, `ui_draft_playlist`, `manual_selection_draft`, `draft_binding`, `saved_playlist`, `saved_playlists`, `bootstrap_mode` |
| Routing | `pending_action`, `validated_plan`, `validated_route` |
| Page context | `page_context`, `page_info`, `current_article_id`, `current_article_content`, `current_video_transcript` |
| Clarification / resolver | `resolver_context`, `resolver_status`, `resolver_option_id`, `resolver_value`, `resolver_confidence`, `clarification_response` |
| Sharing / LMS | `selected_lms`, `share_action` |

**Who writes what, in flow order:**

| Node | Writes |
|---|---|
| Fetching user profile | `user_profile` |
| Validating & detecting input | `draft_playlist`, `bootstrap_mode`, `manual_selection_draft` |
| Enriching selected playlist | `topics`, `search_keywords` |
| Setting bootstrap playlist title | `draft_playlist`, `manual_selection_draft` |
| Resolving pending answer | `turn_status`, `turn_resolution`, `resolver_context`, `resolver_status`, `resolver_option_id`, `resolver_value`, `resolver_confidence` |
| Resolving your answer (LLM) | `resolver_status`, `resolver_option_id`, `resolver_value`, `resolver_confidence` |
| Planning request & clarifications (LLM) | `last_intent`, `topics`, `requested_count`, `selected_lms`, `share_action` |
| Validating action readiness | `validated_route`, `validated_plan`, `pending_action`, `draft_binding`, `draft_playlist`, `manual_selection_draft` |
| Analyzing your Topic (LLM) | `search_keywords` |
| Searching JoVE library | `topics`, `available_count`, **`curation_context`**, `pending_topic` |
| Building curated response | `phase`, `available_count`, `requested_count`, `draft_playlist`, `selected_lms`, `topics`, `saved_playlist`, `pending_topic`, `draft_binding` |
| Building edit response | `phase`, `available_count`, `requested_count`, `draft_playlist`, `selected_lms`, `topics`, `saved_playlist` |
| Building direct response | same as above, plus `pending_topic`, `pending_action`, `draft_binding` |
| Normalizing saved playlist | `phase`, `saved_playlist`, `saved_playlists`, `draft_playlist`, `topics`, `draft_binding`, `pending_action` |

## Two things worth raising in the meeting

**1. `curation_context` is not declared in the Start node's state.** It is written at runtime by the search node and read by the curation node as `$flow.state.curation_context`, but it is missing from the 37 declared keys — the only such key in the flow, and also the largest payload. It works today, but it is the one piece of state with no declared initial value, so a path that reaches curation without passing through search would hand the model an unresolved variable.

**2. Rich context exists in state but never reaches the curation model.** `current_article_content`, `current_video_transcript`, `page_context`, and `user_profile` are all carried in flow state, and the search step even retrieves excerpts and thumbnails — yet the model choosing the playlist sees only id + title + article type, with no chat history. If curation quality is the topic of the meeting, that is the lever: the selection decision is being made on titles alone.
