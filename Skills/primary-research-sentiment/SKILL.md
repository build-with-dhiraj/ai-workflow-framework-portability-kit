---
name: primary-research-sentiment
description: >
  Use when onboarding/grading an Indian stock and you need LIVE ground-truth — retail
  due-diligence, management-call commentary, and community sentiment — to corroborate or
  disconfirm a dossier. This is the finance-desk "channel-checker / primary-research
  harvester" (role #4, the weakest leg). Harvests ValuePickr forum DD, Reddit sentiment
  (via the Reddit MCP), screener.in earnings-call transcripts, and optional employee
  sentiment into extracted/research/source_captures/<TICKER>_primary_research.md. It is
  LIVE DD CONTEXT for the Stage-1 dossier + the forensic screen — NOT vault atomics, and
  it NEVER sets verdict/conviction/MoS (the Munger/Buffett vault is the binding arbiter).
  Triggers: "channel check <ticker>", "what does ValuePickr/Reddit say about <ticker>",
  "primary research on <ticker>", "harvest sentiment", "ground-truth this dossier",
  "management call red flags".
---

# Primary-Research / Channel-Check Harvester (finance-desk role #4 — the *weakest leg*)

The desk's job here is **ground-truth**: what do people who actually use the product, attend
the concalls, and dig into the filings say — does it *corroborate* or *disconfirm* the dossier?
This is the only finance-desk role with **no canonical free data source** (no Bloomberg/Refinitiv
equivalent for retail), so it is the *weakest leg by design*. Treat its output as **questions to
verify**, never as fact, and never let it move a grade.

**This leg earns its keep ONLY by disconfirming** (`[[primary-research-earns-edge-only-by-disconfirming]]`).
Because markets aggregate public information efficiently, a harvest that *confirms* a popular long adds
nothing — that view is already priced. The only durable contribution is (a) a fact that **disproves** a
pillar of the thesis (a moat-bust, a channel breakdown), or (b) a checkable **hard fact / forensic lead**.
Frame every run as an attempt to break the thesis, not to cheer it.

## What this is / isn't (read before running)
- **Output = LIVE DD CONTEXT**, written to `extracted/research/source_captures/<TICKER>_primary_research.md`
  — exactly like the existing dossier/source captures. It feeds **Stage 1 (dossier / understanding)**
  of `stock-onboarding-pipeline` and the `forensic-accounting-redflags` screen as *corroboration /
  disconfirmation*.
- **It is NOT vault atomics.** Do **NOT** write to `vault/canon` or `vault/perspectives`, do **NOT**
  touch the brain index. Munger/Buffett (the binding CIO via `32_consult_brain.py`) remain the **sole**
  arbiter of verdict, conviction and MoS. This skill supplies *context*, never a *verdict*.
- **Weakest-leg honesty (state it in every capture).** Indian retail community quality varies wildly;
  ValuePickr & Reddit are self-selected and often talk-their-book; concalls are management's own framing.
  Weight every signal with human judgment and down-weight it hard against the vault.
- **Epistemic ceiling (the EMH limit — state it too).** Public chatter about a well-followed name is mostly
  *already in the price*. So this harvest's only durable output is a **disconfirmation** or a **checkable hard
  fact** — never a confirmation of a crowded long. A glowing forum consensus is not a buy signal; at most it is
  a sentiment-froth datum (see STEP 5). This is the binding resolution of the efficiency tension: Damodaran's
  efficiency view is cited here to *limit* the skill's claims, never to license acting on crowd information.

## Division of labour: the SCRIPT does the cheap scrapes, YOU do the MCP + judgment
- **Script** (`data/scripts/61_harvest_primary_research.py`) does the parts that are scriptable and
  cheap: paginated ValuePickr capture (Discourse `.json` API), screener.in transcript-PDF discovery +
  `pdftotext` extraction, and a generic-web fallback that **reuses `capture_web` from
  `60_ingest_external.py`** (defuddle → Apify). Apify spend ≈ $0 (defuddle/JSON first).
- **You (the agent)** do what a standalone script *can't*: the **Reddit step (Reddit MCP)** and the
  final **synthesis**. A script has no MCP access, so the Reddit pull is agent-only — this is explicit
  in the generated file.

## STEP 0 — Frame the harvest as disconfirmation (+ pull the standing arbiter frame)
Before scraping, **write down the dossier's core bull thesis in one line**, then run the whole harvest as an
explicit attempt to *disprove* it. Anchoring to the existing view is the failure mode here
(`avoid-anchoring-and-destroy-previous-ideas`); a harvest that only confirms is flagged as anchoring and
**re-run with bear-case queries** ("<company> problems / fraud / churn / competition / promoter").

Then pull the standing arbiter frame from the desk/binding layer via `--corpus blended` — it admits the
desk atomics alongside the binding mentors, kept on relevance to the query:
```bash
set -a && source /Users/Dhiraj/dev/invest/.env && set +a && /Users/Dhiraj/dev/invest/.venv/bin/python \
  /Users/Dhiraj/dev/invest/data/scripts/32_consult_brain.py \
  --company "<name> primary research disconfirming channel checks promoter credibility" --model general --step understanding --corpus blended \
  --json-out extracted/grilling/<TICKER>_primary.json
```
This surfaces `[[primary-research-earns-edge-only-by-disconfirming]]` and `[[loudest-promoter-is-least-credible-source]]`
ALONGSIDE the binding arbiter atoms (`beware-fraudulent-information-sources`, `do-not-talk-up-your-investments`).
The desk atomics are connective tissue, not a vote — they **never** set verdict/conviction/MoS.

## STEP 1 — Run the harvester (ValuePickr + screener, scriptable)
First find the ValuePickr thread URL (web-search `forum.valuepickr.com <company>` — the thread id is the
number in `/t/<slug>/<id>`). The screener URL is derivable from the ticker. Then:
```bash
set -a && source /Users/Dhiraj/dev/invest/.env && set +a && /Users/Dhiraj/dev/invest/.venv/bin/python \
  /Users/Dhiraj/dev/invest/data/scripts/61_harvest_primary_research.py \
  --ticker <TICKER> \
  --valuepickr-url "https://forum.valuepickr.com/t/<slug>/<id>" \
  --screener-url   "https://www.screener.in/company/<TICKER>/consolidated/"
```
This writes `extracted/research/source_captures/<TICKER>_primary_research.md` with the ValuePickr
bull/bear raw signal + the discovered transcript links, and leaves clearly-marked TODOs for the Reddit
and synthesis steps. It is **idempotent** — re-runs read the cache under
`data/apify_runs/_primary_research/<TICKER>/` and re-spend nothing (use `--force` to re-fetch).
Notes:
- ValuePickr topic pages are JS-rendered, so `defuddle`/`capture_web` return 0 chars — the script uses
  the **Discourse `.json` API** instead (free, structured, richer). It captures the *latest* N×20 posts
  (recent sentiment is what matters); raise `--max-vp-pages` for more history.
- Transcript PDFs are hosted off-site (investor-relations / primeinfobase / BSE). Reachable ones are
  `pdftotext`-extracted (free); unreachable hosts are **recorded as links** in the file for you to fetch
  (browser, or the `capture_web` Apify fallback) — never silently dropped.

## STEP 2 — Reddit sentiment (AGENT-ONLY, Reddit MCP)
A standalone script has no MCP, so **you** run the Reddit MCP directly (`mcp__reddit-search__*`):
```text
mcp__reddit-search__search_reddit(query="<TICKER> stock", limit=10, sort="relevance")
mcp__reddit-search__search_reddit(query="<company name>", subreddit="IndiaInvestments")
# then for the best DD/sentiment hits:
mcp__reddit-search__get_post_comments(post_id="<id>")
```
Useful India subs: `IndiaInvestments`, `IndianStockMarket`, `DalalStreetTalks`. Capture a **3–5 bullet
sentiment gist**: net bullish/bearish, recurring concerns, any on-ground channel checks.
- **Source-weighting (apply to every forum/Reddit/concall voice):** rank credibility **inversely** to how
  hard the voice talks its book (`[[loudest-promoter-is-least-credible-source]]`, `do-not-talk-up-your-investments`).
  Down-weight the loudest promoters by default; prefer skin-in-the-game, specific, disconfirmable claims over
  costless cheerleading. A confident price target is the *weakest* kind of signal; a verifiable on-ground
  fact (a closed store, a lost client, a delayed payment) is the strongest.
- **If the MCP rate-limits (HTTP 403/429 — common):** retry with backoff, narrow the query, or fall back
  to `WebSearch` over `reddit.com`. Confirm the server with `mcp__reddit-search__test_reddit_mcp_server`.
- **Reddit Responsible-Builder policy:** corroboration only — no de-anonymising users, no model-training
  use, no cross-posting. Read-only.

## STEP 3 — Management-call red/green flags (screener transcripts)
Read the extracted transcript(s) in `data/apify_runs/_primary_research/<TICKER>/` (or fetch the recorded
links). Pull:
- **RED:** guidance cuts, evasive/non-answers, pricing-power erosion, churn, rising receivables/promoter
  pledge, related-party deals, "growth at any cost" tone, blaming macro for everything.
- **GREEN:** candid acknowledgement of misses, durable pricing power, capital discipline, owner-operator
  language, consistent multi-year framing.
This is the input that most usefully overlaps with `forensic-accounting-redflags`. The **top tripwire** is
not generic "earnings-quality concern" — it is **cash conversion**: does the concall narrative of profit
show up as cash? Route any growth-without-cash, rising-receivables, or aggressive-revenue-recognition signal
straight to the **CFO/PAT** check (`[[channel-check-as-forensic-tripwire]]`, `owner-earnings-as-quality-proof`:
high, stable CFO/PAT corroborates management integrity; a widening gap is the lead to chase against the
filings in the forensic screen).

## STEP 4 — Employee sentiment (optional, low weight)
Check `ambitionbox.com` / `glassdoor.co.in` for the company: overall rating, attrition, leadership churn,
culture flags. An **execution-quality proxy only** — weight near zero unless it corroborates a
transcript/forum concern.

## STEP 5 — Synthesise into the capture file (hedged)
Fill the "Synthesis for the dossier" block: ValuePickr bull/bear (+ open questions), Reddit gist,
mgmt-call red/green flags, employee-sentiment note, and a **hedged net read** ("corroborates /
disconfirms the dossier because …, BUT this is the weakest leg — verify independently"). Then point the
Stage-1 dossier author and the forensic screen at this file. **Do not** translate any of it into a
conviction/verdict/MoS number — that is the vault's job.
- **Read the crowd contrarily** (`[[crowd-sentiment-read-inversely]]`, `be-fearful-when-others-are-greedy`):
  record the net sentiment as a **contrarian** datum — unanimous euphoria is a yellow flag (froth, already
  priced), capitulation/disgust is a potential window. **Subordinate to the gates:** a capitulation signal is
  a window *only after* the binding moat + owner-earnings checks pass; contrarianism on a genuinely broken
  business is just catching a falling knife. This datum never overrides the fundamental verdict.

## How it plugs into the onboarding pipeline
- **Stage 0/1 (dossier & understanding):** run this harvester for each NEW stock alongside the
  Substack-article capture; the dossier's "Comment-thread red flags" / ground-truth context section
  cites it. It is *context for understanding*, parallel to — never above — the binding circle-of-
  competence consult.
- **Forensic screen:** transcript red flags + ValuePickr fraud/governance chatter feed
  `forensic-accounting-redflags` as leads to verify against filings.
- It changes **no** grade. After running, the normal binding consult (`--corpus binding`) and the v2
  conviction/MoS/inversion gates proceed unchanged.

## Hard rules
1. **Output is LIVE DD context, never binding.** Write only to
   `extracted/research/source_captures/<TICKER>_primary_research.md`. Never write vault atomics, never
   touch the brain index, never set/adjust conviction, verdict or MoS.
2. **Reddit is agent-only (MCP).** The script cannot do it; you must. Honour the Responsible-Builder
   policy and handle 403/429 gracefully (retry/backoff/WebSearch fallback).
3. **Reuse, don't rebuild.** Generic web URLs route through `capture_web` (`60_ingest_external.py`);
   prefer free paths (Discourse `.json`, `pdftotext`) so Apify spend stays ≈ $0. Never write empty
   captures — record a blocked source as a TODO link instead.
4. **State the weakest-leg caveat in every capture.** Community quality varies; this is corroboration /
   disconfirmation, requiring human judgment to weight — not a thesis, and not a substitute for the
   Munger/Buffett CIO.
5. **Attribute, quote sparingly, never fabricate.** Quote ValuePickr/Reddit by username and date; if a
   source returns nothing, say so and count it — never invent sentiment or a transcript quote.
6. **Disconfirm or surface a hard fact — don't echo.** The edge is disconfirmation
   (`[[primary-research-earns-edge-only-by-disconfirming]]`); a pure confirmation of a crowded long is
   already priced and worthless. But disconfirmation-first must NOT tip into motivated bear-hunting: a
   *manufactured* red flag is no more binding than a manufactured bull case (rule 5 still governs). Weight
   voices inversely to how hard they talk their book. The desk atomics
   (`vault/desk/primary-research/atomic/…`) are connective tissue you cite via `[[slug]]` — you do **not**
   create or edit them, and they never cast a verdict vote.
