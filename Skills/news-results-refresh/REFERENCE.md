# news-results-refresh — Reference

Workspace: `/Users/Dhiraj/dev/invest`. Env: `set -a && source /Users/Dhiraj/dev/invest/.env && set +a`; Python: `/Users/Dhiraj/dev/invest/.venv/bin/python`.

## Sweep universe (FULL dashboard ∪ held, derived LIVE each cycle)
The loop sweeps the **FULL Action Dashboard (~241 names)**, not just the ~90 INDmoney holdings.
```bash
# 0. BUILD the sweep universe from the LIVE dashboard col B (READ-ONLY; degrade-safe).
#    Re-derives data/manifests/dashboard_universe.json every cycle → onboarded rows auto-join.
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/build_sweep_universe.py
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/build_sweep_universe.py --dry-run  # inspect, no write
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/build_sweep_universe.py --test     # fixture self-test
# prove what the detector sweeps (full dashboard ∪ held) + dump coverage:
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/70_detect_material_events.py --universe
```
- Resolver `data/scripts/held_universe.py` exposes **`sweep_tickers()`** = `dashboard_universe.json.resolved` ∪ `held_universe.json.resolved`, degrade chain **dashboard → held → legacy** (each with a loud stderr warn; never a silent shrink). `held_tickers()` (owned-only) is UNCHANGED, still used where the owned distinction matters (AVOID-owned→SELL col-N word).
- `dashboard_universe.json` (TRACKED): `generated_at`, `source:"dashboard:colB(live)"`, `resolved:[...]` (sweepable dashboard tickers w/ dossier), `held:[...]` (resolved ∩ held), per-ticker `{dossier, brain_model, company, held}`, `no_dossier:[...]` (data rows lacking a dossier — expect ~0), `alias_resolved` (e.g. `ZOMATO→ETERNAL`, `IGIL→IGI`). Legend rows (≥246) are excluded; aliases resolve via dossier `aliases:` then a small verified map.

## Commands (the chain)
```bash
set -a && source /Users/Dhiraj/dev/invest/.env && set +a

# 1. DETECT — material events over the sweep universe (full dashboard ∪ held) → SQLite index
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/70_detect_material_events.py

# 2. CONSULT THE BINDING BRAIN (when a MATERIAL event fires) — vault is CIO
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/32_consult_brain.py \
  --company "<name>" --model <bank|consumer-brand|commodity-cyclical|utility-psu|capital-goods|platform|general> \
  --step <conviction|margin-of-safety|verdict> --corpus binding \
  --json-out extracted/grilling/<TICKER>_refresh.json

# 3a. L1 WRITE-BACK — head-window edit only (HEAD_LIMIT=4000, never tail-append)
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/apply_head_window_grade.py <grade>.json
# 3b. L2 — do NOT apply. Write a proposal instead:
#     data/state/pending_reviews/<TICKER>.json  (human approves later)

# 4. REINDEX + RECALL CANARY (floor 0.95, auto-revert on drop)
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/26_build_lancedb_index.py

# 5. (L1 only) propagate the refreshed one-liner to the Sheet "Why" column
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/extract_dashboard_why.py
```

### Dynamic-IV + guarded re-rank chain (earning-power event; PR #33)
```bash
# Is this event an EARNING-POWER change (→ IV re-grade) or just price/flow/sentiment (→ IV untouched)?
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/coln_iv_event_gate.py --test

# Price-INDEPENDENT fundamental IV by brain_model (DCF / justified-P/B / mid-cycle). --test proves two prices → identical IV.
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/80_estimate_iv.py --test

# 71 IV-event branch is invoked by the normal orchestrator run (dry-run default; --apply re-freezes the head only).
# The whole-set re-rank + publish is the GUARD, default-OFF. In the LOOP it is invoked by 73 stage 3c
# (gated by RERANK_AUTO=1 AND brain-healthy post-reindex (SKIP_PUBLISH!=1) AND >=1 L1 applied this cycle):
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/82_rerank_guard.py --tag <tag>          # dry-run + assertions + order-diff, NO live write (RERANK_AUTO OFF)
RERANK_AUTO=1 /Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/82_rerank_guard.py --tag <tag>   # SUPERVISED live re-rank (guarded + auto-revert)
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/82_rerank_guard.py --self-test

# A re-rank CARRIES the live col-D verdict + col-M conv byte-for-byte; if those disagree with the dossier
# oracle, 82's carried-cell assertion ABORTS. Reconcile them first with the sanctioned col-D/col-M writer
# (default dry-run; COL_DM_DASHBOARD_WRITE=1 + omit --dry-run to write live):
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/sync_col_dm.py --only <TICKER[,TICKER...]>   # dry-run plan, NO live write
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/sync_col_dm.py --test
node /Users/Dhiraj/dev/invest/tools/sheets-bridge/write_col_dm.mjs --self-test
```

### col-N news-aware quick-read + daily drift audit (PR #31/#32/#34)
**col-N is published for EVERY dashboard row** — including AVOID / board-contradiction / `needs_review` names, analysed and filled exactly like any other stock (user directive 2026-06-26). The **binding Munger/Buffett CIO (vault) verdict is PRIMARY and is what col-N shows**; the **56-director board panel is ADVISORY and NEVER vetoes col-N**. 78's Gate 7 RECORDS any board (mis)alignment as a non-blocking signal (into `board_contradictions`, also surfaced by `81`); it never fails verification on a contradiction. 79 publishes whenever a VALID col-N can be synthesized and skips ONLY: `verdict==NEEDS_REVIEW`, a genuinely THIN dossier (BOTH best AND worst NEEDS_REVIEW), no rendered string, or head_overflow. A board contradiction / governance flag / within-tier `needs_review` is a CONTESTED GRADE that still publishes the current verdict's col-N and is recorded for human adjudication — never withheld.
```bash
# 📰 segment (read-only): latest material event → dated factual verdict-neutral clause
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/coln_news_segment.py --test
# col-N maker → checker (Gate 8 re-derives the 📰 segment) → sanctioned single-column writer
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/77_synthesize_dashboard_why.py --universe sweep --apply --force
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/78_verify_dashboard_why.py
COL_N_DASHBOARD_WRITE=1 /Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/79_publish_col_n.py   # omit the env var for dry-run
# read-only whole-set consistency audit (writes nothing; exit≠0 on a class-1/2/5 drift; --strict gates all)
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/81_audit_dashboard_consistency.py
```

## Autonomy ladder (user override 2026-06-25: L2 IV/conviction/verdict-demotion + re-rank now AUTO under the guard)
| Level | Trigger | Action | Auto? |
|---|---|---|---|
| L0 | every swept name | stamp `last_event_checked: <today>` | ✅ auto |
| L1 | MATERIAL event, no grade change | one-line catalyst/"Why" head-window edit → Sheet "Why" + col N (77→79) | ✅ auto |
| L2 | IV change / `conviction_level` / **verdict DEMOTION** / within-tier / MoS recompute (earning-power event) | Stage-3 re-grade in `71` (binding consult + `80_estimate_iv` + conviction gates + MoS recompute + verdict re-derive + board sanity-check) → re-freeze head → **`73` stage 3c invokes `82_rerank_guard.py --tag headwindow`** re-rank + publish | ✅ auto **under `RERANK_AUTO=1` (ENABLED in the plist 2026-06-25; code default still OFF) AND brain-healthy AND ≥1 L1 applied** |
| — | **FOREVER *promotion*** / `needs_review` / board-contradiction (GRADE change only) | proposal → `data/state/pending_reviews/<TICKER>.json` | ❌ human-gated (the SOLE GRADE gate; **col-N still publishes** for the current verdict — the board is advisory, never a col-N veto) |

The re-rank goes through `82_rerank_guard.py` (3-tab backup + dry-run-diff + ticker-keyed checksum + auto-revert + maker≠checker) — **never a silent or raw re-rank**. In the loop it is invoked by **`73_refresh_cycle.sh` stage 3c** (once per cycle, after the reindex), gated by `RERANK_AUTO=1` **AND** brain-healthy post-reindex (`SKIP_PUBLISH≠1`) **AND** ≥1 L1 applied this cycle; `71` never calls it per-ticker. **`RERANK_AUTO=1` is ENABLED in the LaunchAgent plist (2026-06-25)** so the scheduled loop's stage 3c re-ranks live (guarded). The CODE default is still OFF: a manual `82` run without the env var dry-runs + asserts + prints the order-diff, then STOPS (no live write); the plist supplies `RERANK_AUTO=1` for the cron. The carried col-D verdict / col-M conv are reconciled to the dossier oracle ahead of a re-rank by the sanctioned writer `sync_col_dm.py` → `write_col_dm.mjs` (2-column assert + inverted checksum + per-row diff + backup + auto-revert + `COL_DM_DASHBOARD_WRITE=1`). **IV = earning power only:** price / FII / MF flows / ratings / buy-calls fail `coln_iv_event_gate.py` → they move live MoS/Upside (cols I/J/K) but NEVER IV or the rank.

## Event index — SQLite schema
`data/state/event_index.sqlite`, table `events`:
`ticker, event_date, event_type, severity, source, url, headline, first_seen, applied_state`
with **`UNIQUE(ticker, event_date, headline)`** (NOT url — INDmoney Source-A news items have null `url`, so a url-based key would never dedup). Inserts use `INSERT OR IGNORE`, so re-runs add 0 dup rows and never clobber `first_seen`. The run cursor lives in a sibling **`swept`** table (`ticker, last_event_checked`), advanced via `ON CONFLICT(ticker) DO UPDATE` — NOT a `news_refresh_state.json` file (that was plan-era wording; the SQLite `swept` table is the cursor of record). Applied events (`applied_state` set) are never re-emitted as new. **Idempotency proven Phase 3 (2026-06-22): run2 → new_rows=0, dups=0, first_seen stable, cursor=today.**

### Deterministic idempotency regression check (Phase 3)
```bash
# isolated built-in self-test (temp DB, no network): asserts run1=2 new, run2=0 new, dup=2
/Users/Dhiraj/dev/invest/.venv/bin/python data/scripts/70_detect_material_events.py --test
# OR replay the fixed cached dump against a throwaway DB copy (real state untouched):
TMP=$(mktemp -d); cp data/state/event_index.sqlite "$TMP/t.sqlite"
/Users/Dhiraj/dev/invest/.venv/bin/python data/scripts/70_detect_material_events.py data/state/news_dump_mvp.json --db "$TMP/t.sqlite" | grep items=
/Users/Dhiraj/dev/invest/.venv/bin/python data/scripts/70_detect_material_events.py data/state/news_dump_mvp.json --db "$TMP/t.sqlite" | grep items=  # expect new_rows=0
rm -rf "$TMP"
```

## Materiality taxonomy
`data/config/event_taxonomy.json` — types RESULTS / DEAL / FILING / GOVERNANCE → severity {INFO, MATERIAL, RED}; drop price-commentary / listicles. GOVERNANCE-RED escalates (aligns with `forensic-accounting-redflags`). Detector source order: Tier-0 INDmoney `news` (live probe; never fabricate) → screener.in results/concall dates → BSE/NSE corporate-announcements → moneycontrol (noisy, last).

## Frontmatter contract
- `last_event_checked: YYYY-MM-DD` on every swept dossier (L0).
- HEAD WINDOW = frontmatter snapshot + one-line thesis in the first ~4,000 chars. Edits live here ONLY.

## File map
| Path | Role | Status |
|---|---|---|
| `data/scripts/70_detect_material_events.py` | detector (maker); sweeps `sweep_tickers()` (full dashboard ∪ held); `--universe` coverage report | ✅ built (Phase 1; universe-expanded) |
| `data/scripts/apply_head_window_grade.py` | head-window write-back | ✅ reused |
| `data/scripts/32_consult_brain.py` | binding-vault consult | ✅ reused |
| `data/scripts/26_build_lancedb_index.py` | reindex + Recall canary | ✅ reused |
| `data/scripts/extract_dashboard_why.py` | one-liner → Sheet "Why" | ✅ reused |
| `data/scripts/build_sweep_universe.py` | sweep-universe builder — LIVE dashboard col B → `dashboard_universe.json` (READ-ONLY, degrade-safe, `--test`/`--dry-run`) | ✅ built |
| `data/manifests/dashboard_universe.json` | tracked sweep manifest (full dashboard ∪ held source) | ✅ built |
| `data/scripts/held_universe.py` | resolver — `sweep_tickers()` (dashboard ∪ held) + `held_tickers()` (owned-only), degrade-safe | ✅ extended |
| `data/manifests/held_universe.json` | tracked HELD manifest (owned, from INDmoney via `73_refresh_held_universe.py`) | ✅ built |
| `data/config/event_taxonomy.json` | materiality rules | ✅ built |
| `data/state/event_index.sqlite` | event index | ✅ built |
| `data/state/pending_reviews/<TICKER>.json` | L2 proposals | created on first L2 |
| `data/scripts/71_refresh_orchestrator.py` | maker (routes L0/L1/L2 incl. the IV-event Stage-3 re-grade branch) — dry-run default, `--apply` re-freezes the head, `--apply-sheet` (off) for Sheet "Why", `--test` self-test; FOREVER-promotion/needs_review/board-contradiction → `pending_reviews/`; re-rank is delegated to `82` (RERANK_AUTO-gated, never called from here) | ✅ Phase 4 + IV branch (PR #33) |
| `data/scripts/72_verify_refresh.py` | checker (independent of 71) + boolean stop condition; IV gates re-derive the proposed IV is brain-grounded + price-independent + board-aligned + sane-bounded + FOREVER-routed, `--test` self-test | ✅ Phase 4 + IV gates (PR #33) |
| `data/scripts/coln_iv_event_gate.py` | earning-power-vs-sentiment discriminator (arms the IV re-grade; price/FII/MF/ratings/buy-calls → False), `--test` | ✅ built (PR #33) |
| `data/scripts/80_estimate_iv.py` | price-INDEPENDENT fundamental IV by `brain_model` (DCF / justified-P/B / mid-cycle); binding-brain-grounded slugs; `compute_iv` cold-start fallback only; `--test` proves two prices → identical IV | ✅ built (PR #33) |
| `data/scripts/82_rerank_guard.py` | the ONLY thing allowed to re-rank the LOCKED dashboard — wraps the Stage-6 publish runbook behind 3-tab backup + dry-run-diff + ticker-keyed checksum + auto-revert; `RERANK_AUTO=1` (**code default OFF; ENABLED in the LaunchAgent plist 2026-06-25 → live on the scheduled loop**), `--self-test`. **Invoked in the loop by `73` stage 3c** (gated by RERANK_AUTO + brain-healthy + ≥1 L1 applied); never called from `71` | ✅ built (PR #33) + wired into 73 + plist-enabled |
| `data/scripts/sync_col_dm.py` / `tools/sheets-bridge/write_col_dm.mjs` | sanctioned col-D(verdict)/col-M(conviction) sync — reconciles the carried D/M cells to the dossier oracle so a guarded re-rank passes 82's carried-cell assertion. Default dry-run; `COL_DM_DASHBOARD_WRITE=1` to write; 2-column assert + inverted checksum (excl. {3,6,8,10,11,12,18}) + per-row diff + backup + auto-revert; `--test`/`--self-test` | ✅ built |
| `data/scripts/77_synthesize_dashboard_why.py` / `78_verify_dashboard_why.py` / `79_publish_col_n.py` | col-N news-aware quick-read: maker (`--universe sweep`) → checker (Gate 8 re-derives 📰; **Gate 7 board-alignment is ADVISORY, recorded not blocking**) → sanctioned writer `write_col_n.mjs`. **col-N published for EVERY row incl. AVOID/board-contradiction** (binding-CIO verdict is what shows; board panel never vetoes); 79 skips ONLY verdict==NEEDS_REVIEW / thin (both clauses NR) / no-render / head_overflow | ✅ built (PR #31/#32) + col-N-for-every-row (board advisory) |
| `data/scripts/coln_news_segment.py` | read-only 📰 segment (latest material event → dated factual clause; never fabricates) | ✅ built (PR #32) |
| `data/scripts/81_audit_dashboard_consistency.py` | read-only daily drift auditor (re-derives col-N/verdict/📰/rank vs source of truth; WRITES NOTHING; gates exit on class-1/2/5) | ✅ built (PR #34) |
| `tools/sheets-bridge/write_col_n.mjs` / `write_col_l.mjs` | sanctioned single-column writers (col N / col L) — single-column assert + inverted checksum + auto-revert + env flag | ✅ built (PR #30/#31) |
| `data/state/refresh_log.jsonl` | append-only refresh log (cursor of record = SQLite `swept` table) | ✅ Phase 4 |
| `data/state/pending_reviews/<TICKER>.json` | L2 proposals (README + _EXAMPLE.json tracked; live proposals gitignored) | ✅ Phase 4 |
| `STATE.md` (`loop-pause-all`) | kill-switch | ✅ Phase 4 |
| `com.invest.news-refresh.plist` | daily LaunchAgent ~17:00 IST | ⏳ Phase 5 |
| 🔄 Refresh-Log side tab | visible staleness log (NOT the dashboard) | ⏳ Phase 5 |

## Phase status
1. **MVP** — detector + manual head-window round-trip — ✅ DONE (STLTECH deal detected MATERIAL; BEL head thickened; AWL→KEEP, TEXRAIL→SELL re-grades).
2. **Encode the SKILL + rule amendment** — ✅ THIS skill + `stock-onboarding-pipeline` HARD RULE #1 Exception B.
3. **State idempotency** — ✅ DONE (2026-06-22): proven on the detector with no code change. run2 → new_rows=0, no dup keys, `first_seen` byte-stable, `swept` cursor advances to today, applied events not re-proposed. Regression check above (`--test` / replay).
4. **Gated loop** — ✅ DONE (2026-06-22): `71` maker + `72` checker (independent) + pending queue + L0/L1/L2 + `STATE.md` kill-switch. Exit gate PASS, independently verified: forced L2 delta → `pending_reviews/<TICKER>.json` PENDING; dossier head byte-identical; Sheet/dashboard never touched (72 has zero Sheet refs; 71's only Sheet path is print-only behind off-by-default `--apply-sheet`, no re-rank logic exists); kill-switch no-ops. Both have `--test` self-tests. Open Low findings: zero-IV head_patch slips the schema gate; UNIQUE-key is headline not url (fine until BSE/NSE feeds add URLs).
5. **Schedule** — ✅ `com.invest.news-refresh.plist` daily ~10:00 (L0-only on cron); monitor cron log + token budget.
6. **Universe expansion** — ✅ DONE (2026-06-25): sweep universe is now the **FULL Action Dashboard (~241)** ∪ held, re-derived LIVE each cycle. New builder `build_sweep_universe.py` (READ-ONLY on dashboard, degrade-safe, `--test`) writes tracked `data/manifests/dashboard_universe.json` (241 resolved, 0 no_dossier, `ZOMATO→ETERNAL`). Resolver gains `sweep_tickers()` (dashboard ∪ held; degrade chain dashboard→held→legacy); `held_tickers()` unchanged. `70`/`71`/`72` sweep/verify `sweep_tickers()` (det. `--universe` = 243; 71 routes 243; 72 stop-condition checks all 243). `73_refresh_cycle.sh` runs the builder FIRST (stage 1b) so onboards auto-join; builder failure leaves the chain running on the last good manifest. All `--test` green; dashboard never written.

## Anti-patterns (designed out)
No unattended 24/7 loop (kill-switch) · no self-grading (maker≠checker) · no full-context re-prompt · **no silent dashboard mutation** (every write goes through a sanctioned single-column writer or the guarded full re-rank `82` with auto-revert; `RERANK_AUTO=1` ENABLED in the plist 2026-06-25, code default still OFF) · no auto FOREVER-promotion (the sole human GRADE gate) · **col-N never vetoed by the advisory board panel — published for every row incl. AVOID/board-contradiction (binding-CIO verdict is what shows)** · no IV move on price/FII/flow/rating/buy-call · no early-exit on empty universe (empty = success) · no tail-append edits · no fabricated event/citation/IV.
