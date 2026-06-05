---
name: jove-youtube-feed-pipeline
description: >
  End-to-end pipeline for feeding YouTube channels into the "Connecting Dots" second brain
  (Dhiraj's JoVE knowledge system): enumerate → pre-flight gate → Apify transcribe →
  connect_youtube (filter→NER→index→related→[[JoVE]]) → LanceDB queryable → Pinecone archive.
  Use when the user wants to ingest YouTube channels/playlists/videos into the vault, run a
  multi-channel "feed round," estimate Apify cost, or deepen existing channels. Covers the
  8-voice JoVE stakeholder framework, the autonomous batch runner, and the hard-won reliability
  rules. Triggers: "feed the brain", "ingest these channels", "round N feed", "transcribe this
  channel/playlist", "how much will Apify cost".
---

# JoVE YouTube → Brain Feed Pipeline

The proven, repeatable process for turning YouTube content into queryable brain knowledge. Built + battle-tested across Rounds 1–3 (~8,500 transcripts).

## The architecture (do NOT deviate)
**Enumerate + gate for FREE; pay Apify only for transcripts.**
1. **`yt-dlp --flat-playlist`** enumerates a channel/playlist (FREE, no API key). Resolves @handles → channel IDs. This also powers the gate + top-N selection.
2. **Pre-flight gate** (`workers/preflight_channel.py --source ytdlp`, $0 — gpt-4.1 + metadata): identity check + junk filter + cost forecast → **GO/NO-GO before any spend**.
3. **Apify** (`workers/apify_youtube_ingest.py`) transcribes GO channels via the `supreme_coder/youtube-transcript-scraper` actor (~$0.0005/captioned video, pay-per-result). Modes: `--channel`, `--playlist`, `--video`, `--watch`; `--top-n N` caps giants; omit for full. Idempotent via `data/youtube_channels.json` registry. Token: `APIFY_API_TOKEN` in `.env` (free tier $5/mo).
4. **`workers/connect_youtube.py --all`** enriches: filter (8-voice relevance) → NER (gpt-4.1) → **LanceDB index** → related-linker → link-to-`[[JoVE]]`. Idempotent (skips connected).
5. **LanceDB** = the vector leg → queryable via `workers/ask_brain.py`.
6. **Pinecone archive** (jove-memory / conversations namespace) — wrap-up summary of the round for future recall.

## The 8 stakeholder voices (ranking lens)
Rank channels by *voice fidelity* (a real end-user speaks) × *strategic weight to Dhiraj's mandate* (author acquisition + editorial workflow + biopharma).
🎓 young researcher · 🔬 PI/author · 🖋 editor/reviewer · 🏭 biopharma/R&D · 📚 librarian/buyer · 👩‍🏫 instructor · 💰 grants · ⚔️ competitor.
Source of truth: `vault/context/jove/youtube-import-runbook.md` (v3).

## Running a feed round (autonomous, batched)
1. Build a scope file like `data/round3_scope.json`: batches → channels `{name, ref (channel_id|@handle|playlist_id|video_id), mode (channel|playlist|video), expect}`. Group by voice/priority. `expect` is the gate's identity string — make it accurate (a too-narrow expect causes false NO-GO).
2. Use the batch runner pattern (`data/round3_runner.py`): for each batch → ingest all channels → `connect_youtube --all` → **validate (errors=0, fragments<500 or HALT)** → next. Idempotent + resumable.
3. Launch detached: `PYTHONPATH=. nohup .venv/bin/python data/round3_runner.py &`. Supervise via **ScheduleWakeup** (resume-proof), NOT a background bash watcher (those die on session resume).
4. On completion: scorecard + ask_brain sanity query + Pinecone archive.

## Cost math
`videos × $0.0005` (pay-per-result; captionless = not charged). ~97% caption rate on academic channels, but **podcast/conference channels are largely captionless** (e.g. a 1,191-video podcast yielded 250). So *landed ≈ scope × ~0.75* for podcast-heavy scopes. Free tier = $5/month.

## Hard-won rules (violate these and it breaks)
- **A YouTube @handle ≠ the brand.** Always verify actual channel content/ID before ingesting. Traps caught: `@benchfly` = a music band; `@elife` = kitchenware; `@protocolsio` doesn't exist (real = `@zappylab`); two "Andy Stapleton"s (one's a motorcycle vlogger). The pre-flight gate exists because of this.
- **LanceDB: NEVER per-row `merge_insert`.** It fragments the table (Round-2 hit 7.5 GB / 31,997 fragments → stalls). The fixed indexer batches upserts + `optimize()` + ANN + body-only content hash. The scale test (`tests/workers/test_lancedb_scale.py`) asserts fragments < 50 and fails on regression. Fragment count is the canary — watch it.
- **Body-only content hash** for change detection (frontmatter stamps like `connected_at`/`related_at` must NOT trigger re-embeds).
- **Relevance filter = the 8 voices**, not "lab/research only" (the old narrow filter wrongly quarantined instructors/grants/librarians).
- **Idempotent + resumable everything** — long runs span session resumes; re-launching must continue from registry state, never double-spend.
- **Builds run via orchestrator-dispatched worktree subagents + inline review** — NOT fresh-chat couriering (lossy handoffs cause wrong-file mistakes).
- **Slugs must include video_id** (else same-title videos overwrite each other).

## Key files
- Workers: `apify_youtube_ingest.py`, `preflight_channel.py`, `connect_youtube.py`, `lancedb_indexer.py`, `related_linker.py`, `ask_brain.py`
- Scope/runner exemplars: `data/round{1,2,3}_voice_seed.json`, `data/round3_scope.json`, `data/round3_runner.py`
- Runbook: `vault/context/jove/youtube-import-runbook.md` · Memory: `memory/project_youtube_feed_status.md`
- Plans: `planning/APIFY-YOUTUBE-INGEST-DISPATCH.md`, `planning/LANCEDB-RELIABILITY-PLAN.md`
