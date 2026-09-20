---
name: jove-labs-sweep
description: On-demand deep sweep that reconstructs the entire JoVE Labs state from every surface in knowledge/jove-labs/surfaces.yaml (vault and Google Docs, Slack, Gmail, calendar, tl;dv and Granola, GitLab code, Jira and Confluence, Mixpanel and Redash, Figma, the QA and Champions sheets, Linear) into the canonical knowledge/jove-labs/STATUS.md brief. Proves its own coverage arithmetically, reports whether it is converged with the other Claude account, flags stale or redundant docs for confirmation, and routes action items to Linear and Jira. Every invocation covers ALL surfaces, delta-only against the stored cursors; if that does not fit one context it runs as a Workflow, never as a smaller sweep. Invoke when Dhiraj says "labs sweep", "reconstruct jove labs", "what is the state of jove labs", "what happened on labs", "catch me up on labs", or /jove-labs-sweep.
---

> **Project root:** every relative path in this skill (`knowledge/...`, `tools/...`, `.claude/skills/...`) resolves against `~/dev/jove-hq`, never the current working directory. This skill is invocable from any cwd, so prefix accordingly: `~/dev/jove-hq/knowledge/jove-labs/STATUS.md`.

# JoVE Labs sweep (the project-brain rebuild)

Purpose: Dhiraj should never have to tell Claude what happened on JoVE Labs. It was all recorded. This skill reconstructs the full picture from every surface into one canonical brief (`knowledge/jove-labs/STATUS.md`) so any session reads that instead of being fed context.

This is not the belt's daily sweep. The belt routines (08:06 `jove-open-work-sync`, 19:09 `jove-ppp-eod-draft`) are scheduled, delta-based, and all-work. This one is project-scoped, on-demand, deep, and its job is cross-source reconciliation plus doc hygiene. Read ownership per surface is in the precedence table in `_shared/jove-connectors.md`.

**What changed in v2 (8 Aug 2026).** Surfaces are data, not prose: they live in `knowledge/jove-labs/surfaces.yaml`. State lives in the repo at `knowledge/jove-labs/.sweep/`, not in the home directory, so both Claude config dirs converge on it. Coverage is asserted arithmetically instead of narrated. A run now says out loud whether it is converged with the other account.

## `/jove-labs-sweep` means every surface, always (Dhiraj, 13 Aug 2026)

**Standing instruction, and it overrides the group-scoping section below.** When Dhiraj
invokes this skill by name, the run covers **all five groups and every enabled surface in
`surfaces.yaml`**. There is no such thing as a partial run by choice any more. Scoping to
one group is allowed only when he names the group in the same breath.

**If it does not fit in one context, that is not a reason to cover less. It is the reason
to use the `Workflow` tool.** He gave standing authorization for it here, in his own words:
*"if this require batches then start a workflow to have the sweep run end to end of all
surfaces."* That opt-in is scoped to this skill, and it does not generalise to other work.

Shape of the workflow, when one is needed:

- One phase per group, `comms`, `trackers`, `docs`, `code`, `metrics`. Use `pipeline()`, not
  `parallel()`, because no group's read depends on another group's results, and a barrier
  would only add wall-clock.
- One agent per surface, or per small cluster of surfaces that share a connector and a cursor.
- Every agent is handed **its surface's cursor and fingerprint from `state.json` and its
  existing findings from `findings.md`**, and is told to return only the delta plus a coverage
  row. An agent that re-derives what the ledger already holds has burned its budget for nothing.
- The orchestrator does the join pass, the reconcile and the write-back. Subagents never write
  `state.json`, `findings.md` or `STATUS.md`, or they will clobber each other.
- The coverage arithmetic is still per-surface and still mandatory. A workflow that returns 41
  of 43 rows is a `partial` run that must say so, exactly like a single-context run.

**Delta, never reconstruction.** This is the mechanism that makes full coverage affordable,
and it already exists in gate steps 2 and the fingerprint table: read what is stored, pull
only what moved, write the new and changed on top. A full sweep is expensive only when it
re-reads unchanged surfaces, and gate step 2 plus the fingerprint check are what stop that.
Rebuild from scratch only when `state.json` is missing or unparseable.

## Gate (run first)

1. Read `knowledge/jove-labs/surfaces.yaml`. This is the scope. A surface absent from it is out of scope; a surface in it that this run does not report is a finding, never silence.
2. Read `knowledge/jove-labs/.sweep/state.json`. It holds per-surface cursors and fingerprints and it is your prior: never re-pull what it already covers. Pull only the window after each cursor. If it is missing or unparseable, ignore it and do a full reconstruction, then rebuild it at write-back. A bad cache can only cost duplicate work, never missed items.
3. Read `_shared/jove-connectors.md` before pulling any live data.
3a. Read `knowledge/jove-labs/.sweep/findings.md`. It is what is currently believed about Labs and it is the prior for every finding this run will make. Then run **both** health gates; a non-zero exit from either is reported with the coverage breach, not as a footnote:
   - `node tools/vault-index/health.mjs` — is the semantic mirror still a mirror.
   - `node tools/sweep/claim-check.mjs` — **does any document still assert something we have since settled otherwise.** This is the one check that is not delta-shaped. Every other mechanism here asks "what moved?"; a stale document that never moves is invisible to all of them, which is exactly how a PI-facing FAQ kept telling researchers the trial ran six months for three weeks after 90 days was verified in code (F-014, F-015). Contradictions are a finding, and the fix is the document, not the allow-list.
   - `node tools/sweep/thread-check.mjs` — **were Slack threads actually opened, or only parents.** Exits non-zero on any surface read parents-only. A surface reported `OK` with unread threads is the specific false confidence that has now cost three misses.
   - `node tools/sweep/finding-clock.mjs` — **does anything need a human today, and does it have one.** The other gates ask whether the SYSTEM is honest. This is the only one that asks whether the PRODUCT is in trouble. It failed on its first run with three launch-blocking findings three days from launch and F-003 unowned, while every other gate was green.
   - **Register-app ingest (before pulling, after the other gates).** Two action sources
     during the transition, both drained every run: (1) the repo inbox
     `knowledge/jove-labs/.register-app/actions-inbox.json`, written by the Vercel app's
     Save button, and (2) until the Vercel app is verified live, the interactive artifact
     (URL in the register frontmatter `app:`) via WebFetch of its `register-actions`
     block. Apply per `tools/register-app/README.md`: close/reopen only WITH a probe at
     the row's closing surface, notes verbatim, asks into the run's work queue; applied
     actions are removed from the inbox in the same commit. At write-back, rerun
     `node tools/register-app/web/scripts/gen-data.mjs` and commit the regenerated
     `src/data/register.json` so the next push deploys fresh data; the git-connected
     Vercel project (jove-labs-register) redeploys on every push to master. An action
     ignored is Dhiraj's instruction dropped; an action applied without a probe is F-253
     again. Both are findings. After the write-back push deploys, run
     `node tools/register-app/audit.mjs`: any STALE/BEHIND/UNSWEPT row is a finding, because
     the register app is Dhiraj's stated single source of truth and a stale app misrepresents
     the vault to its one reader.
   - `node tools/sweep/claim-subject-check.mjs` — **does every code-backed outbound draft say
     which object each claim was checked on.** Two facts verified on two different objects,
     fused into one sentence, produced a claim to a stakeholder that a feature was broken when
     the feature did not exist (19 Aug, JVA-31347). Form checks cannot catch a wrong subject, so
     the table carries an explicit Subject column and a line naming what is NOT claimed. The same
     error recurred once after the first fix, which is why the subject is now its own column
     rather than something the writer is trusted to hold in mind.
   - `node tools/sweep/provenance-check.mjs` — **does every live draft carry its stitched
     source timeline.** A draft written from one surface while another surface holds the
     newer or fuller word is the failure this catches (19 Aug: a ticket drafted from a call
     transcript alone while the morning's Slack DM carried the requirement).
   - `node tools/sweep/ledger-health.mjs` — **did every prior run's findings actually reach the ledger.** Drift here means an earlier run swept surfaces and taught nobody, so this run's prior is incomplete and its own findings may be re-derivations of work already paid for. Fix the drift before pulling, or you will pay for it twice.

3b. **This run is accountable to the ledger.** At write-back it must do exactly one of two things: add its findings and list its `run_id` under `runs_ingested`, or list it under `no_new_findings` with a reason. Do not stamp the id at the gate, only once findings exist. Silence is the single outcome the gate rejects, and it is the one that has already happened once.
3e. **Surface discovery (added 15 Aug 2026, system v3 P3: the Wispr-class fix made structural).**
   Before pulling, enumerate the data sources this session can actually see: every connected
   MCP server whose tools read a data store (meetings, mail, docs, tickets, analytics), plus
   `mcp-registry list_connectors` when available. Diff that list against `surfaces.yaml`.
   **Any data-bearing source with no registry entry is a finding this run must report**, with
   a proposed entry, never a silent skip. Bought by the incident: Wispr Flow held the 14 Aug
   the Director 1:1 in full transcript while every sweep saw only "a huddle started", and it was
   found because Dhiraj asked, not because the system looked. Infrastructure services
   (Pinecone, GitLab-as-transport) are not surfaces; anything holding words people said or
   wrote is.

3d. **Read `knowledge/jove-labs/roadmap.md` before ranking anything.** Its `phase` flag decides the question this run is asking: **pre-launch** asks *will it work*, **launch** asks *is it working now*, **post-launch** asks *is anyone using it, where do they drop, which institution is stalling*. Coverage tells you the surfaces were read. The roadmap tells you which of them mattered. A run that reports "no breach" while a launch-blocking finding sits unowned has measured integrity and missed consequence, which is exactly what happened on 11 Aug.

3b-bis. **Is every recording a note? `node tools/meetings/coverage.mjs`.** The three meeting
recorders (tl;dv, Wispr, Gemini) are all `critical` surfaces, and a sweep that reads a call from
one of them while the vault holds no per-meeting record of it is reasoning from a source the next
run cannot find. Exit 1 lists uncoupled conversations: report them in the coverage table and name
PPP STEP 1c as the owner (this skill never writes meeting notes). Exit 2 means a snapshot is stale
or missing, so a recorder went unread, which is a coverage breach in its own right.

3c. `knowledge/jove-labs/INDEX.md` is the map of the 248-note corpus, one line each, newest first. Read it before searching the folder or querying the index: it is cheaper than a semantic query and it shows what exists, which a similarity score cannot. It is generated, so never hand-edit it; fix the source note's frontmatter `subject` instead.
4. Read `~/dev/jove-code/.kernel/KERNEL.md`. **If a brief and the kernel disagree, the kernel wins.**
5. Write `last_run.status: "in_progress"` with this run's `run_id` and enabled count **before the first pull**. That is the first durable write, per CLAUDE.md rule 10, so a limit-death mid-run loses at most one surface. **Stamp the skill version in the same write:** run `node tools/sweep/skill-version.mjs` and copy `skill_commit`, `skill_sha256` and `skill_dirty` onto `last_run`. A skill is loaded into context at invocation, so an edit made mid-session never reaches a run already in flight, and without the stamp a run that *predated* a rule is indistinguishable from one that *ignored* it. Runs 2104Z and 2118Z on 10 Aug are exactly that case. `skill_dirty: true` means uncommitted rules were in force, which is the one state nobody can reconstruct later.
6. On-demand only. Never schedule it, never run it at session start, never loop it.

`run_id` is `<UTC compact timestamp>-<account short name>`, for example `2026-08-10T2053Z-gmail`.

**Probe the account, do not infer it (added 13 Aug 2026).** `node tools/jove-drive/account.mjs --json` returns the work account behind the connectors. That value, and only that value, goes on `last_run.account`. The session system prompt reports Dhiraj's **Claude subscription** email, which is a different identity and has been quoted as the answer repeatedly. Global rule at the top of `~/.claude/CLAUDE.md`.

**Probe the capability, do not infer it from a notice (added 27 Aug 2026).** Same shape as the account rule above, and it cost a whole sweep. A session-start notice listed `plugin:productivity:slack`, `plugin:productivity:atlassian`, `plugin:productivity:linear`, `plugin:figma:figma` and `GitLab` as needing authorization. Those are the **plugin duplicates**. The live claude.ai connectors carry hashed-UUID tool names (`mcp__c6399901-…__slack_*`, `mcp__564fb47c-…__searchJiraIssuesUsingJql`, `mcp__cd286948-…__list_issues`, `mcp__Figma__*`) and were authenticated the whole time. The run declared 31 of 70 surfaces BLOCKED, wrote off all of Slack, Jira, Confluence, Linear and Figma, and reported a partial sweep on the day Labs went live to 365 institutions. Nothing in the notice was false; the inference from it was.

So, before any surface is recorded `BLOCKED (capability)`:

1. **One live call against that connector, and paste its result.** `slack_read_channel` on `C0XXXXXXXXX`, `getAccessibleAtlassianResources`, `list_issues` with no filter, `get_metadata` on the Labs file. A `BLOCKED` row whose evidence is a notice rather than a failed call is malformed and does not ship.
2. **A duplicate server name is not the server.** Match the tool name you would actually call, not the human-readable label in a notice. Two entries can carry one product's name and only one of them is wired.
3. **GitLab reads live via the PAT** at `.claude.json` → `projects/<repo>/mcpServers/gitlab/env/GITLAB_PERSONAL_ACCESS_TOKEN`, and `tools/jove-code-sync.sh` fetches the clones over SSH regardless of MCP state. `~/.claude/jove-code-sync/last-sync.json` carries `remote_sha` per repo, so clone freshness is a fact to read, never a caveat to assume. The MCP needing OAuth has never been a reason to fall back to a stale clone.
4. **Read the extraction, not just the regex.** The first PAT probe here returned 401 because a loose `glpat-` regex over the whole config grabbed a malformed match. Pull the value by its key path and check the length before concluding a credential is dead.

A capability claim is a claim like any other and takes the same evidence as a finding.

**Identity is the account, never the config dir (corrected 10 Aug 2026).** Dhiraj switches accounts by logging out of the Claude desktop app and back in as the other one, on the same machine and therefore in the *same* config dir. Keying identity on the config dir made both accounts look identical, so the cross-account check could never fire. Record `account` on `last_run` and stamp `updated_by` with the account, not the directory. State the account at the start of the run; never infer it from the app (CLAUDE.md, accounts and pools).

The two accounts: `personal-account@example.com` (Max) and `work-account@example.com` (personal seat plus the JoVE org seat). The JoVE account is the one that holds the work connectors.

## Convergence check (before any finding)

Both accounts run on the same machine and share `state.json` on disk. That file, not the chat, is how the second account knows what the first one saw, and it is why switching accounts mid-effort costs nothing. Print this block first, always.

Read `last_run` from `state.json`. If `account` differs from the account running now, this is a cross-account run and the verdict matters. Classify every difference into exactly one of three buckets. Never merge them, they mean different things.

- **DRIFT** the world moved since the prior run. Expected and healthy. Every DRIFT row must carry a timestamp **after** the prior run's `last_ok` for that surface. A DRIFT row timestamped before it is a GAP wearing a disguise, and you say so.
- **GAP** the prior run never covered this surface, evidenced by its own coverage row. This is the only status that proves a defect in the skill rather than movement in the world. It is what the two-account test is actually checking.
- **REGRESSION** same window, different fingerprint, so one of the two runs read wrong. Two documented live instances of this class: the Confluence `contentFormat` fallback silently returning markdown with no anchors, and reading `main` instead of `feat/JVA-29725` (that second instance is historical, 5-11 Aug 2026 only; since the 12 Aug merge the rule inverted and main is correct).

Verdict line: `CONVERGED` requires zero GAPs, zero REGRESSIONs, and every DRIFT row timestamped after the prior `last_ok`. The assertion is not zero events; on live surfaces, real movement between two runs is correct.

**Under CONVERGED the run is read-only.** No STATUS edit, no Linear ticket, no Jira comment. It still writes its receipt and still refreshes `last_ok` per surface, which is what keeps the staleness rule honest, and it still prints the coverage table.

## Surfaces

Pull every surface in `surfaces.yaml` whose `consumers` include `labs-sweep`, in parallel where the tool allows, each windowed by its cursor in `state.json`.

- A `binding_rule` on an entry **is binding**. Read it before pulling that surface. It exists because someone already got this wrong.
- A surface with `fidelity: verbatim` gets the DM fidelity rule below.
- A surface whose `owner` is anyone but Dhiraj is **read-only**. The Champions sheet is CS's, the bug tracker is the QA lead's. Propose rows to Dhiraj; never write them.
- `reachable: false` or `unknown` still gets a row in the ledger every run, with its reason. An unreachable surface is a reported gap, not an absence.
- **`critical_nodes` is the point of the surface, not a detail of it.** Where an entry lists them, resolving each one is the job: pull the surface, resolve every node, and write the name and today's date back into the surface's `cache`. A node whose `name` is null has never been resolved by anyone; report it as unresolved and **never infer a name from its id**.
- **`cache` first, network second.** If an entry has a `cache`, read it before pulling. If the surface is unreachable for this account, the cache is the answer: report those items as STALE with their last-verified date, not as unknown. If the surface IS reachable, pull, then write what changed back to the cache so the account that cannot reach it still benefits.

### Capability is per account, so failure needs an owner

The two accounts do not have the same connectors. Figma and GitLab in particular
work on one and not the other. So a surface that cannot be read is not simply
failing, and recording it as `FAIL` loses the only fact that matters: whether the
*other* account could have read it.

Three distinct outcomes, and they must not be merged:

- **FAIL (data)** the surface is reachable and the read genuinely broke. Retrying on the other account changes nothing.
- **BLOCKED (capability)** this account lacks the connector or the authorization. Record the account in `blocked_for` and mark it **HANDOFF**: the next run on the other account picks it up first, ahead of its own priority order.
- **FAIL (unknown)** never probed, so which of the two is unknown. Probe before classifying.

A run that ends with open HANDOFF items says so in its receipt and in the STATUS
block, naming the account that should take them. That, not the coverage count, is
what makes switching accounts worth doing rather than merely survivable.
- Slack is one registry entry (`slack.registry`) pointing at `knowledge/memory/slack-surface-registry.md`, which is the sole authority for Slack IDs and owns the read-once cursor contract. Never copy its tables into this skill or into `surfaces.yaml`.

Every finding must come from a live tool result. Cite or abstain, per surface.

### Doc hygiene (vault docs and Google Docs)

Per file, one verdict: superseded-by (a newer doc covers the same ground), duplicate-of, untouched-since (old mtime, no inbound wikilinks), or contradicts-a-current-decision.

Output a list: file, verdict, reason, recommendation (archive to `projects/_archive`, merge into X, or delete). **Never auto-delete or auto-archive. Flag it, Dhiraj confirms, then act.** Some of these docs are not yours to remove and a wrong delete is hard to reverse.

### DM fidelity rule (added 17 Jul 2026, after a scope decision in a the dev lead DM was compressed into a half-wrong bullet)

Any DM or channel message that changes a scope, a decision, or a ticket's meaning is quoted VERBATIM in the output: speaker, timestamp, exact words, and the ticket id the thread names. The sweeping agent must read the actual thread via `slack_read_channel` (threads and context, not just the search snippet) before summarizing it. A decision-bearing message that arrives in the report as a paraphrase is a defect: the 16 Jul miss kept "co-trainer invites are lab-level" and dropped the sentence that actually settled scope ("Then this ticket's scope is only for module and lab level upload csv").

Which surfaces this fires on is declared in the registry (`fidelity: verbatim`) and marked per row in the Slack registry, so a new surface inherits the rule by declaration instead of by someone remembering.

### Never skip a live surface because another routine touched it today (added 13 Aug 2026)

**The incident.** Dhiraj posted a Slack thread at 12:44 IST. A delta sweep run at ~16:50 IST
was told *"do not re-read Slack, the belt already covered it today"* and missed it entirely.
Three causes stacked, and only the third is the actual rule violation:

1. ~~Two independent cursor stores~~ **CLOSED 15 Aug 2026 (system v3 P2): there is ONE
   Slack cursor value store, `~/.claude/jove-watchdog/slack-cursors.json`, keyed by
   conversation id (C*/D*; U-id keys are legacy belt aliases).** Sweep readers take their
   cursor from it **READ-ONLY. AMENDED 26 Aug 2026, and this is a deliberate REVERSAL of
   the 15 Aug one-store-two-writers arrangement, logged as such: only the belt advances
   this file (08:06 and 19:09; the registry contract in `jove-connectors.md` is the
   authority). The sweep never writes it.** Why the reversal: the sweep is Labs-scoped and
   the sink is all-work, so a mid-day sweep advance moves the sink's window past the Director/
   squad Slack that is not Labs, and that signal has no other route into the PPP row or
   day-prep (Cursor-Eater). The registry contract's own guard (advance only if no
   later-slotted belt run has stamped) cannot see a sweep, because the sweep correctly
   never stamps the belt cache, so the old arrangement was unguardable, not merely costly.
   Duplicate Labs-Slack delta reads are the accepted, cheaper cost. The per-channel files
   under `.sweep/slack/` carry verbatim notes ONLY, never cursor values; `state.json`'s
   `slack.registry` rollup mirrors the max timestamp this sweep **OBSERVED** for coverage
   arithmetic, which may run ahead of the belt cursor it read from. A reader that
   takes a cursor from anywhere else is re-introducing the F-141 defect.
2. Even within this skill's own store, a per-channel file can be current while the parent
   rollup entry in `state.json` is stale, if the rollup is not re-written in the same edit.
   Reconcile the rollup to the child files, every write-back, not only at the gate. (Post-26-Aug reversal this rollup is the sweep's ONLY Slack cursor write, and it lives in `state.json`, never in `slack-cursors.json`.)
3. **The rule this incident sets.** `slack.registry` is `cadence: live`. A live surface is
   marked so precisely because a cursor-delta pull on it is cheap, which means it is never
   correct to skip it on the theory that "it was read recently by something." Read it fresh
   from THIS skill's own cursor, every run, no exception for same-day activity on another
   surface's clock. The cost of the delta is what makes full coverage affordable; skipping it
   is what makes coverage claims false.

### Threads are mandatory, and the cursor cannot see them

**This section was two sections saying the same thing, written 10 and 11 Aug. That is
itself the symptom: a rule restated is a rule nobody is executing.** Merged 11 Aug, and
the enforcement moved out of prose into `tools/sweep/thread-check.mjs`.

`slack_read_channel` returns PARENT messages only. Reading it is not reading the surface.
Every miss of this class has been identical: the parent was captured, the reply that
settled the question was never opened.

**The incident that made it binding.** On 8 Aug Dhiraj posted the P0 that the 90-day
trial is never granted. the dev lead replied *in-thread*: "I've migrated the dev data to
preview. Subscription issues should be fixed. Please verify." That reply is the entire
state of the item. It says the fix was a data migration rather than the code change the
ticket asks for, and it says verification had not happened. Three sweeps read that
parent, printed `Reply count: 2` in their own output, and none opened it.

**The incident that proved prose alone does not work.** On 11 Aug a Haiku workflow read
30 surfaces under instructions that included this rule. On the QA group DM it opened
**3 of 50 threads** and reported the surface `OK`. It then produced the headline
"P0 trial bug (domainArticleIds fix deployed)" whose only support in the file was
Dhiraj's own bug report ending "Fix: send domainArticleIds in the sync request" — a
PROPOSED fix turned into a deployment claim. Believed, it would have retracted F-001.

Binding, on every Slack surface:

1. **Any parent with a non-zero reply count gets `slack_read_thread` on its ts.** Not the
   interesting ones. Every one. If a surface has 50 parents with replies, that is 50
   thread calls; budget for it rather than sampling.
2. **A reply outranks its parent.** Where they disagree the reply is current state. Quote
   the reply.
3. **The cursor is the latest activity timestamp including replies, never the newest
   parent.** This is what made the failure permanent rather than occasional: a reply added
   later to an older parent carries a timestamp *behind* a parent-keyed cursor, so a delta
   sweep passes it correctly by its own rules and can never recover it.
4. **State-tag every decision-bearing item**: `PROPOSED` / `DECIDED` / `DONE` / `DISPUTED`,
   each with the exact words that establish it. "Fix: do X" in a bug report is PROPOSED.
   "I deployed X" is DONE. "Please verify" means verification was **requested**, not
   performed. The 11 Aug fabrication was a missing distinction, not carelessness.
5. **`threads_opened < parents_with_replies` is `PARTIAL`, never `OK`.** Report it as
   `PARTIAL (parents only, N threads unread)`. **Enforced by
   `node tools/sweep/thread-check.mjs`, which exits non-zero.** Counting a surface as
   covered while its threads are unread is the false confidence this ledger exists to
   prevent, and the coverage arithmetic will otherwise sum clean while it happens.

## Which model does which part (added 11 Aug 2026, measured)

Work here has three kinds and they do not cost the same. Running all three on the
expensive model is the structural waste; running all three on the cheap one loses the
findings that matter.

| Part | Who | Why |
|---|---|---|
| **Reach** a connector (Slack, Jira, Confluence, Drive, Figma) | Claude. Haiku for `normal` surfaces, **Sonnet for anything `critical` or `verbatim`** | Only a Claude agent holds these connectors. Azure cannot see them at all. |
| **Grind**: read what was fetched, extract, classify, cross-reference, draft | **Azure `gpt-4.1` via `tools/sweep/az.mjs`** | No tools needed, just reading. Budget is effectively unlimited, so work that was previously unaffordable (every transcript, the whole Slack history, the 64-meeting doc) is now free. |
| **Judge**: reconcile contradictions, decide what matters, write anything a stakeholder reads | The expensive model, deliberately | This is where every miss in this skill's history happened. |

**The split is measured, not assumed.** On 11 Aug Haiku read 30 Slack surfaces well on
quiet ones (15 of 15 threads on `#triage-product-support`) and **degraded exactly where
content was densest**: 3 of 50 threads on the QA group DM, no thread accounting at all on
the two highest-decision surfaces. It compresses instead of quoting when there is a lot to
read, which inverts the value: the surfaces most worth reading get the shallowest reads.
Azure, asked to classify the same the dev lead reply, correctly returned `fix_type: "data"` —
the distinction that took a full exchange to establish for F-001 — and simultaneously got
the verification nuance wrong. Strong extraction, soft judgment, in one test.

So: cheap for breadth, Sonnet for the surfaces the registry marks critical or verbatim,
Azure for volume, expensive model for the call. A cheap model's output is an input to
judgment, never a finding on its own.

## Reconcile (the core value)

A decision in Slack, a Jira status, a doc claim, and the code about the same thing are ONE reconciled item, resolved to the latest verified state, not four items. Surface contradictions explicitly. Keep tracking the live tensions until they are ratified: the reopened clone model for hand-over, and the North Star framing (module completion versus activation).

**A question asked repeatedly is one unresolved item, not several closed ones.** Counting four askers as four answered rows hides a risk. If the same thing is asked more than once across a call or a channel, it is unresolved regardless of how confidently it was answered, and it gets code-verified before it is reported as settled.

### The join pass (mandatory, added 17 Jul 2026 after two synthesis misses)

Reconciliation failed twice on 17 Jul not because retrieval missed anything but because synthesis reported findings grouped BY SURFACE (Slack bullets, Jira bullets, GitLab bullets) instead of BY OPEN ITEM, so cross-surface connections had no structural home. Both misses had every piece already retrieved: a the engineer DM about "the questions" was filed as housekeeping instead of being joined to the editorial-questions action item sitting in two coupled meeting notes and STATUS itself; a the dev lead DM scope quote was never joined to Dhiraj's own in-session statement or to the commit message ("csv export api for labs and modules") that matched it.

Before writing STATUS, run this explicitly:

1. Build the join list: every open item in STATUS's machine block + every open item in KERNEL.md + every action item from coupled meeting notes of the last 7 days + every decision or instruction Dhiraj gave in the current session + the drafted-but-unposted ledger.
2. For every new finding, ask "which existing item is this about?" and attach it there. A finding may be reported standalone only after it fails to match everything on the join list.
3. Report findings grouped by open item, each item carrying all its surfaces' evidence together (the meeting note that created it, the Slack message that moved it, the ticket that should record it, the commit that built it).
3b. **Never create a Jira ticket without searching Jira first (CLAUDE.md rule 13, added 15 Aug 2026 after this skill's session created JVA-31257 a day after QA had already filed the same bug as JVA-31255).** QA and developers file tickets on their own; a defect this sweep observed may already be theirs. JQL-search by symptom keywords and scan the epic's recent children before any `createJiraIssue`. An existing ticket gets linked and, where our evidence is stronger, its OWN reporter keeps it and the evidence goes to Dhiraj to pass on, never a parallel ticket.
4. An action item from a coupled meeting note is a live object: it stays tracked until completion evidence appears on some surface, and every sweep re-checks each one across ALL surfaces, not just the surface it was born on. "Prepared questions for a meeting" has a lifecycle: asked or not asked at the meeting, if not what happened next, track to done.

### Per-open-item verification (deltas are not enough)

Every sweep enumerates the open items in STATUS's machine block and marks each one: verified-still-open / resolved (evidence) / changed (evidence). An open item that no surface mentioned this window is still explicitly re-verified, not silently carried. Delta-only sweeps let items rot between windows.

### Commit-to-ticket cross-check

Any new commit or MR whose message names a JVA id gets that message (and diff, when cheap) compared against the ticket's current description and the latest decision on record. State the result explicitly: MATCHES the agreed scope / CONTRADICTS it / ticket description lags a decision that exists elsewhere (name where). Never report "code shipped ahead of ticket clarity" without first checking whether the scope was already communicated on another surface.

Read the code from `main` in both `jove.com-ui` and `research-svc`, PLUS every open MR touching `src/labs` or `src/features/JoveLabs`, per the binding rule in the registry (rewritten 12 Aug 2026: Labs merged to main, so `feat/JVA-29725` is frozen at its pre-merge tip, and fixes land on follow-up branches before main — MR !119 carries the JVA-31114 quiz fix that is on neither). Reading `main` alone is not enough.

## Never re-read what has not changed (added 11 Aug 2026)

**Audited 11 Aug: fingerprints were populated on 0 of 39 surfaces.** The field was in the schema from day one and nothing ever wrote it, so every run re-read every document in full regardless of whether it had moved. Cursors were doing all the work, and cursors only help append-only surfaces like Slack. For a sheet or a doc, a cursor tells you nothing.

**Cheap change detection, per kind. Ask this before pulling a body:**

| Kind | Fingerprint | Cost |
|---|---|---|
| gdoc, gsheet, gdrive_folder | Drive `modifiedTime` via `get_file_metadata` | one metadata call |
| confluence | `lastModified` from `getConfluencePage` | **one call, body included** |
| jira | `max(updated)` across the JQL result | already in the search you run |
| git_branch | branch head sha | one `rev-parse` |
| figma | node `lastModified` from metadata | one call |
| slack | not applicable, cursors already cover it | free |

**Correction, verified 11 Aug.** The Confluence row above used to read "`version.number`,
one call, no body". Neither half is true of the tool actually exposed: `getConfluencePage`
never returns `version.number`, and it always returns the full body, so there is no
body-free variant to call. The usable fingerprint is the `lastModified` display string.
The saving on that surface is therefore not bytes on the wire, it is that an unchanged
page needs no re-reading, re-reconciling or re-reporting, which is where the real cost was.

**The rule.** Fetch the fingerprint first. If it matches what state holds, record `OK (no change)`, refresh `last_ok`, and **do not read the body**. If it differs, read, then store the new fingerprint. A surface whose fingerprint is unchanged is fully covered for the ledger's purposes; that is not a skip and needs no reason.

This is also what makes the second account cheap. The whole point of sharing `state.json` is that account B inherits account A's fingerprints and re-reads nothing that A already saw unchanged.

**Storage hygiene.** Run receipts are per-run prose; there are seven. They are working notes, not knowledge: anything durable belongs in the findings ledger below, which is the thing later runs and follow-ups actually read. They are excluded from the semantic mirror for that reason, so they no longer compete with the ledger on the ledger's own questions. Receipts older than the last three runs can be deleted once their findings are in the ledger, and git holds them either way. Do not let receipt count stand in for memory.

## The findings ledger, and why this skill does not end when the run does

**The failure this fixes.** A sweep pulls a great deal, writes it into a prose receipt, and the receipt is never read again. The next question Dhiraj asks gets answered from whatever survived in the chat, which on a fresh session or the other account is nothing. So the same fact gets rediscovered, or worse, contradicted. The skill was producing data and destroying knowledge.

**`.sweep/findings.md` is the durable memory.** Not a narrative of a run, a standing ledger of what is currently believed about Labs, with each item carrying how it is known.

Every finding carries: a stable id, the claim in one line, its **bin**, the evidence, the surfaces that touched it, its status, and when it was last verified.

The bins are load-bearing and must never blur:

- **observed** ran it, read it, counted it. Name the command or the file.
- **derived** follows from observed things, by steps that can be shown.
- **assumed** taken from a status column, someone's summary, a pattern, or an earlier session. Not verified here.

The whole trial-grant episode is one bin error. "The row says Resolved" is **assumed**. It rode in the same confident rhythm as the code reads, which were **observed**, and the report inherited the confidence of the wrong bin. A finding whose bin is `assumed` is never reported in the same voice as one that is `observed`.

**Read it at the gate, and read it on follow-ups.** This is the part that makes the skill more than a batch job:

> **Any Labs question after a sweep starts by reading `.sweep/findings.md`, whether or not a sweep is being run.** "What is the state of X", "is Y fixed", "should we do Z" are all answered from the ledger first, then from live surfaces where the ledger is stale or thin. Answering a Labs follow-up without opening it is the same defect as sweeping without reading the cursor.

**EVERY commit this skill causes carries `Surface: code` and stages explicit paths, not just the step-10 one (added 17 Aug 2026, after two of them landed without either).** Step 10 describes the commit at the END of a full sweep, and that was read as the only commit worth governing. It is not. The rule above says Labs follow-ups are answered from the ledger and amend it between sweeps, so **most commits this skill causes are single-finding appends, and those were ungoverned.** Two landed on 17 Aug 2026: `30bab4f1` ("F-187: release and thread state reconstructed for the the CEO-CC update") and `d980b52d` ("F-188: code-verified account of the 14 Aug release"). Neither carried a `Surface:` trailer, and `30bab4f1` also swept `knowledge/copilot/daily-pipeline.md` out of another surface's working tree, where an unrelated doctrine edit was in flight, and pushed it, so that change landed under a findings-update message and lost its provenance.

So, for **any** commit that touches the ledger, whether it is a full sweep, a goal run, a single finding append, or a one-line amendment:

- **`Surface: code` trailer, always.** It is one line and it is what tells four concurrent writers apart.
- **Explicit paths only. NEVER `git add -A`, `-u`, or `.`** Name `knowledge/jove-labs/.sweep/findings.md` and whatever else this run actually wrote. Cowork, Cursor, the belt routines and attended sessions all keep work in flight in this repo, and sweeping a file you did not edit into your commit is the write-lane violation this rule exists to prevent. **If a `git status` shows a modified file you cannot account for, that is somebody else mid-edit: leave it.**
- **Doctrine does not ride with ledger output.** A finding update commits by itself. If the same session also edited `CLAUDE.md`, `daily-pipeline.md`, a belt `SKILL.md` or a soul file, those are a separate commit with their own message, because a doctrine change hidden inside a findings update is invisible in the log to everyone who later asks why the rule changed.
- `tools/belt/lane-guard.mjs` now enforces all three as a `commit-msg` hook, so a violating commit is rejected rather than discovered later. **Do not route around it with `--no-verify`**: if the guard fires here, it is almost certainly right, because this skill's commits are exactly the shape it was built from.

**Read it with `ledger-ask.mjs`, not with a vector search (added 13 Aug 2026).**

```
node tools/sweep/ledger-ask.mjs "your question"        # the ledger, entire, one call
node tools/sweep/ledger-ask.mjs --corpus "..."         # plus all 347 notes, sharded
```

The ledger is 67k tokens against a 1,047,576-token window, so the whole thing fits in
one gpt-4.1 call at 6.4% of capacity. **Recall is therefore 100% by construction, and
there is no top-k that can crowd out the answer.** That is not a nicety: every recall
failure this project has had came from ranking. F-014 was a stale GTM doc beating the
verified 90-day answer at 0.892; before that a superseded draft marked "Status: Open"
outranked the ledger entry recording the fix. Ranking exists to avoid reading everything.
Reading everything costs about 12 seconds and one call, so ranking is pure downside here.

`jove-recall` still owns the haystack namespaces, where the corpus genuinely cannot be
read in full. It does not own the ledger any more.

**Maintenance rules.**

- Append and amend, never rewrite. A finding that turns out wrong is **retracted in place** with the reason, because the retraction is worth more than the absence: it stops the next run rediscovering and re-believing it. The Figma restructure claim is the worked example.
- A finding that no surface confirmed this window keeps its old `last_verified` date and gets re-checked, never silently carried as current.
- When two surfaces disagree, that is one finding of type contradiction, not two findings. It stays open until a human resolves it.
- STATUS's machine block is **generated from** this ledger. The ledger is the source; STATUS is the view.

## Scoped runs: cover a slice fully, rather than all of it partially (Dhiraj, 11 Aug 2026)

Every run from 8 to 11 Aug closed `partial`, always for the same reason, and always
skipping the same tail: `slack.registry` sat at 35 of 37 unswept for five consecutive
runs while the surfaces early in priority order were covered every time. 40 surfaces is
more than one run's budget, so the tail was not lower-value, only later.

**Dhiraj's decision, 11 Aug: split the sweep.** Every surface in `surfaces.yaml` now
carries a `group`:

| group | what is in it |
|---|---|
| `comms` | Slack registry, Gmail, calendar, tl;dv, Gemini meeting notes |
| `trackers` | Jira, Confluence, Linear, the sheets |
| `code` | the repos and the kernel |
| `docs` | Google Docs, the Drive folder, Figma |
| `metrics` | Mixpanel, Redash, Clarity, GA4 |

**A run declares its group at the gate and must cover that group completely.** The
coverage arithmetic is per-group, so `complete` becomes achievable again and `partial`
regains meaning: it says a specific slice was not finished, rather than "ran out of
room somewhere". A full sweep is all five groups run in sequence, which is a normal
thing to do across a session rather than an impossible thing to do in one.

**Superseded in part, 13 Aug 2026.** Groups survive as the unit of coverage arithmetic and
as the phase boundary inside a workflow. They no longer license a run that covers one group
and stops. Dhiraj's instruction is at the top of this file: `/jove-labs-sweep` sweeps
everything, and a run too large for one context becomes a `Workflow`, not a smaller run.
Declaring a group at the gate is now only correct when he named that group.

The staleness rule does the rest of the work: a group nobody has run for longer than
its surfaces' `max_age_days` shows up loud, so a neglected slice announces itself
instead of quietly never being reached.

## Absence from a plan is not evidence that something is missing (added 11 Aug 2026)

**The incident.** A coverage audit read the 4 Aug call, found the trial-banner copy fix on no roadmap row, in no PRD section and on no ticket, and proposed filing it as a new High-priority item. It had shipped. The QA sheet said Closed with "Tested & marking it as Closed", the code carried the exact proposed copy at the branch tip, and the findings ledger recorded both commits.

**The invalid inference.** Plan artefacts answer *what do we intend*: the roadmap sheet, the PRD, the tickets, a one-pager. State artefacts answer *what is already true*: the QA and bug sheet, the findings ledger, the code. Absence from a plan has two opposite meanings, not one. Never planned, or planned and done and therefore no longer needing a row. Reading the first meaning and skipping the second is how shipped work gets re-filed.

**Binding, on any claim that something is missing, absent, untracked or not scheduled:**

1. **Check a state artefact before you say it.** The QA sheet first, because that is where shipped work is marked, then the findings ledger, then the code. A gap claim that names no state source checked is malformed and does not ship.
2. **Say what you checked, in the output.** "Not on the roadmap and not in the QA sheet" is a finding. "Not on the roadmap" is a guess wearing a finding's clothes.
3. **Semantic search does not substitute for this.** Proven on 11 Aug: querying the index for the banner returned the 8 Aug draft marked "Status: Open" at 0.870 and did not return the ledger entry that recorded the fix. Recall ranks by similarity, and a superseded draft is often the closest match to the words in a question.

**Two ledger rules follow from the same incident.**

- **A finding's heading carries its status, so the heading is amended with the body.** F-002 read `· OPEN` from 8 Aug while its own body recorded the fix from 10 Aug. Anything read at skim speed was wrong. A heading that disagrees with its body is worse than no ledger entry.
- **A point-in-time draft is marked superseded the moment its content ships.** Tracker rows, ticket drafts and edit plans freeze a status and then compete with current sources in retrieval. Left unmarked they are not merely stale, they actively outrank the truth.

## Coverage ledger (a skipped surface must be impossible to miss)

One row per enabled surface, every run. No summarising "and the rest were quiet".

```
covered + skipped + failed  ==  count(surfaces.yaml where consumers includes labs-sweep)
```

A mismatch prints **first, before any finding**, in this shape:

```
COVERAGE BREACH: registry has N, run reported M.
  Missing: granola.meetings, sheet.champions, jira.jdn-389
```

Per-surface status is one of `OK +N` · `OK (no change)` · `SKIP (<reason>)` · `FAIL (<error>)` · `STALE (<n>d, threshold <m>d)`. A `SKIP` requires a reason string. "Not relevant this run" is not a reason, it is a registry edit.

**Staleness.** `now - last_ok > max_age_days` is a loud finding at the top of the summary, not a table cell. Defaults when the entry omits it: critical 2 days, high 5, normal 14, archive and frozen never. A stale `critical` surface also stamps a warning into the STATUS auto block, so a reader who never saw the chat still sees it.

**Escalation.** `consecutive_failures >= 3` on a critical or high surface opens one Linear ticket, records its id in the surface's `escalated` field, and stops re-reporting it as a fresh finding every run. Escalate once, not daily.

Note the two counts that look alike and are not: `count(surfaces.yaml where consumers includes labs-sweep)` is the yaml denominator, and `slack.registry` is one of those entries which itself expands to the Slack-registry total. Read both counts from their files at run time. Never restate either number here. Never conflate them.

## Output: upgrade STATUS.md (the canonical brief)

Merge idempotently into `knowledge/jove-labs/STATUS.md`. Two zones:

- Human sections, NEVER auto-touched: "Current product frame", "Open items", "Decisions", "Pointers". A July-era human item that August work has closed is a doc-hygiene flag for Dhiraj, not an edit.
- Machine sections, auto-maintained, wrapped in the `jove-labs-sweep:auto` START and END markers:
  - Last swept: UTC timestamp, run id, convergence verdict.
  - Coverage: the full per-surface table.
  - Stale surfaces.
  - State by surface: one short block each for docs, Slack, meetings, code, Jira, Confluence, metrics, design.
  - Open calls and decisions pending, with owner.
  - Contradictions to resolve.
  - Action items, with their Linear and Jira ids.
  - Doc hygiene: the stale and redundant flags for Dhiraj to confirm.

Preserve Obsidian syntax (wikilinks, callouts, frontmatter). Never write the literal auto-block marker text into prose inside the file; it breaks marker detection.

### The mirror is not automatic, and it failed silently for twenty days

**Corrected 11 Aug 2026. The previous instruction here said "do not upsert to Pinecone manually, the PostToolUse hook owns it." That was wrong, and it is the reason this skill could sweep every surface and then not remember any of it.**

The reindex hook lives in `~/dev/jove-hq/.claude/settings.json`, so it only loads when the session is rooted at `jove-hq`. This skill is explicitly invocable from any cwd, and most runs happen from `~/dev`, where that file is not project settings and the hook does not exist. The hook also writes to `/dev/null`, so a run that never fired and a run that succeeded look exactly alike.

What that cost, measured on 11 Aug against the live index:

- **181 in-scope files had never been indexed**, nearly all of them written after 23 Jul: every August meeting read, the tl;dv sweeps, the UAT champion fetches, the milestone records, and `.sweep/findings.md` itself. The durable ledger this skill writes was invisible to every semantic recall.
- **665 chunks belonged to files deleted from disk**, still answering queries as current.
- **STATUS.md held 36 indexed chunks for a 23-chunk file.** Stable ids overwrite `#0..#n-1` and leave the tail forever, so 13 chunks of 22-Jul prose were being retrieved as the current state of the brief. Asking the index "is the trial grant working" returned July's *Ready for QA* above everything, and the August answer in the ledger was not in the top twelve.

**So: verify the mirror, never assume it.**

1. **At the gate**, run `node tools/vault-index/health.mjs`. Non-zero exit is a finding reported with the coverage breach, not a footnote. `--list` names the files, `--fix` prints the repair.
2. **At write-back**, after writing STATUS.md and `findings.md`, run `node tools/vault-index/ingest.mjs --file <relpath>` for each one and read the output. It is idempotent, it trims orphan tails, and it records the file in `tools/vault-index/.index-state.json` so the next health check can prove the mirror is current instead of hoping.
3. **Run receipts are excluded from the mirror by design** (`.sweep/runs`, `.sweep/archive`, `.sweep/cache`). Seven near-identical run narratives compete with the ledger for the same queries and win on surface similarity while carrying none of the current state. `findings.md` is the one file under `.sweep/` that is knowledge, and it stays indexed.

A sweep that leaves the mirror stale has not finished, however complete its coverage table looks. The coverage arithmetic proves the surfaces were read; only the health check proves the reading survived the session.

## Routing

- Linear: read first (`list_issues`, no state filter, issues live in Backlog). A PW item contradicted by live reality is a finding. Every action item that outlives the session goes to the continuation project via `save_issue`, updating an existing ticket over creating a duplicate. Use the `linear-outbox.md` fallback if Linear is unreachable. `PW-\d+` ids never ship in a stakeholder artifact.
- Jira: file new Labs work items as children of epic JVA-29512 in the research squad, reporter Dhiraj Pawar as Product Owner, status Backlog. Update an existing issue over creating a duplicate. Read comments before acting. Any comment that a stakeholder will read passes the stakeholder-write gate in `_shared/jove-connectors.md` first.

## The pre-send check (added 15 Aug 2026, system v3 P3)

**No stakeholder draft ships until the surfaces carrying its recipients' voices have been
delta-read this session.** Run `node tools/sweep/pre-send-check.mjs <names...>` (or
`--draft <file>` to scan the draft for known people); it lists the registered surfaces per
recipient with cursor age. Pull those deltas, then draft. Bought by three incidents in one
week: the VP's rewritten email template sat approved on its own Gmail thread for two days
while the Jira ticket carried the superseded draft; the CS lead's CSM-thread reply was read only
after Dhiraj asked; the 14 Aug 1:1 decisions were nearly contradicted by same-day drafts.
This check is what soul.md rule 10 ("never assume") looks like as a mechanism instead of a
reminder.

## The chat summary (after the artifact is written)

In this order: convergence verdict, then coverage breaches, then stale surfaces, then findings ranked and grouped by open item, then doc-hygiene flags, then the sources pulled and failed. Cite or abstain.

## Write-back (always, even on partial failure)

1. Per surface, in order: pull, write the finding into `.sweep/runs/<run_id>.md`, **then** advance that surface's `cursor` and `last_ok`. Never the reverse. **Slack carve-out (26 Aug 2026 reversal): for surfaces read through `slack-cursors.json`, "advance" means the `state.json` `slack.registry` rollup and `last_ok` ONLY; the sweep never writes `slack-cursors.json` itself, whatever this item says for every other surface class.** A run that dies between the pull and the receipt re-reads that surface next time. Duplicate reads cost tokens; a lost cursor costs messages.
2. On failure: leave `cursor` and `fingerprint` untouched, set `last_error` to the real error string, increment `consecutive_failures`. Never advance a cursor for a surface you did not read.
3. Before each write to `state.json`, re-read it. If `updated_utc` moved and `updated_by` differs from this run, merge per surface rather than replacing the file: for each surface key keep the entry with the later `last_ok`, and take the higher `consecutive_failures`. Entries are independent, so the merge is total and has no conflict case. Stamp `updated_by` (the account), `account` and `run_id` on every write.
3b. **Reconcile state to the registry at the gate.** The registry is authoritative: add a null entry for any surface it has that state lacks, drop any state key the registry no longer carries. A registry that has grown since the last run is not a coverage breach, it is a stale state file, and silently carrying the old count would understate the denominator.
4. Flip `last_run.status` to `complete` or `partial` at the end. A `partial` status is itself a finding the next run reports.
5. STATUS.md machine sections updated, human sections untouched.
6. Linear and Jira write-backs done.
7. Coupling is **not** done here. See the precedence table: `jove-ppp-eod-draft` STEP 1c owns `knowledge/meetings/` and the Supabase `coupled` flag. Whoever couples, flips.
8. **Close the ledger contract, before the index work.** Re-read `findings.md` first: if `updated` moved and `last_touched_by` is not this account, merge per finding rather than rewriting, exactly as `state.json` requires per surface. Then either write this run's findings and add its `run_id` to `runs_ingested`, or add it to `no_new_findings` with a reason. Stamp `updated` and `last_touched_by`. Amend an existing finding in place with a dated line rather than rewriting its body, so a reader can see it moved. **Then run `node tools/sweep/ledger-health.mjs` and require exit 0.** A non-zero exit here means this run is about to commit findings nobody will ever read.
8a. **Rebuild the ledger index: `node tools/sweep/ledger-index.mjs --all` (added 13 Aug 2026).** Runs after step 8 because it indexes what the ledger now says, not what it said before. Four jobs on Azure gpt-4.1, all idempotent, roughly 40 calls and 130k tokens over 112 findings:

   - **`--enrich`** caches, per finding, the questions it answers, its entities, its aliases, and its claim negated. Only findings whose content hash moved are re-enriched. This is what makes cheap lexical search behave semantically **with no embedding model anywhere**, by paying for the semantics once at index time instead of approximating them per query with cosine distance.
   - **`--link`** finds supersedes / contradicts / depends_on / duplicates / evidences edges in ONE pass over all findings, because the compact ledger is only ~4.5k tokens. Contradiction edges are the valuable ones and are printed at the top.
   - **`--gold`** writes the recall-test question for any finding missing one. **This exists because the rule requiring a gold line per finding was broken on 12 Aug: 67 findings were added and zero gold lines, leaving the recall measurement covering 30% of the ledger.** A rule a human has to remember is a rule that fails; this one now runs.
   - **`--audit`** catches the two defect classes the ledger has actually shipped: a heading whose status contradicts its own body (F-002 read OPEN over a body recording the fix), and the same finding filed twice under different ids (F-034 was filed as F-031 by a parallel run). Its first run found seven, three of them created that same day by the append script hardcoding `· OPEN` on every new finding regardless of its state tag.

   **Act on the audit output before committing.** An issue printed and not dispositioned is the same failure as a receipt nobody reopens.

8b. **Rebuild the Obsidian operational views: `node tools/sweep/build-bases.mjs` (added 15 Aug 2026).** Runs after 8a because it renders what the ledger and findings-meta.json now say. Two jobs, both idempotent: push owner/severity/proposed from findings-meta.json into each generated finding note's frontmatter (Bases reads note properties only, so meta that stays in the JSON is invisible to every view), and regenerate the six ops-*.base files under knowledge/jove-labs/. It owns ONLY those: findings.base is hand-styled and never touched. Run it twice and expect 0/0 the second time; a diff on the second run is a bug in the generator, not data. In the same step run `node tools/sweep/build-decisions.mjs` (regenerates the atomic decision notes; every quote is verified verbatim against its source before the note is written, and ids are stable across reruns via decisions/ids.json) and `node tools/sweep/runs-table.mjs` (regenerates knowledge/jove-labs/RUNS.md, the both-accounts run table, from the receipts and the ledger header, so the run history is never a chat-only artifact) and `node tools/vault-index/build-log-hubs.mjs` (added 15 Aug 2026): it regenerates the seven log-hub notes (ppp drafts, tracker hygiene, open work sync, day prep, sprint candidates, appendix drift, meetings) so every dated routine artifact stays linked from a hub and the vault graph never regrows the orphan belt. It owns only those hub files; HOME.md is hand-owned.

9. `node tools/sweep/build-slack-index.mjs` to regenerate the Slack routing table from the per-surface files. **Never hand-write or model-write that index**: the first one was composed by a model summarising other models and carried "P0 trial bug (domainArticleIds fix deployed)" for a surface whose own file says "NOT confirmed deployed". Then `node tools/vault-index/build-map.mjs` to regenerate `knowledge/jove-labs/INDEX.md` and `node tools/sweep/skill-version.mjs --index` to regenerate `.sweep/run-index.md`, then `node tools/vault-index/ingest.mjs --file` for STATUS.md, `findings.md`, INDEX.md and run-index.md, then `health.mjs` to confirm the mirror is clean. Do not rely on the reindex hook; it does not load unless the session is rooted at `jove-hq`.

9a. **When a decision settles, add it to `knowledge/jove-labs/.sweep/claims.json` in the same edit**, with the wordings that contradict it. A settled fact that is not in that file is one nothing will ever check the vault against. Then re-run `claim-check.mjs`.

9b. **Then prove recall actually works: `bash tools/vault-index/eval.sh` (lexical since 15 Aug 2026; the Pinecone gate `retrieval-eval.mjs` is a RETIRED stub).** A present file is not a findable file; this scores Recall@10 with BM25 over the working brain (knowledge minus the YouTube corpus, plus strategy, product, source-docs) against `tools/vault-index/gold-set.jsonl`, and the labs ledger is covered separately by `labs-gold-set.jsonl` scored at the `jove-labs/` root. A miss is a finding, and it names the file that outranked the truth. The first run of the old gate caught a PI-facing GTM doc asserting a six-month trial outranking the verified 90-day answer (F-014); the property being measured is unchanged, only the backend moved when Pinecone was retired. When a finding is added or amended, add or amend its gold-set line in the same edit, or the ledger grows while the measurement stops covering it.

   **Its output is consumed, not filed.** `.sweep/transcript-audit.md` is where it lands, and every `CONTRADICTS` hit gets exactly one of three dispositions before the commit: a new finding, a dated amendment to an existing one, or a recorded dismissal saying why it is not a contradiction. A discovery pass whose output nobody reads is the same defect as a receipt nobody reopens, which is the failure this ledger exists to fix.

   **Noise is a signal about the prompt, not about the corpus.** The first run returned 198 hits and the second 53, and the difference was entirely date-awareness: a 2 Jul note correctly describing the then-current six-month trial is history, not a contradiction. If a run comes back with dozens of hits, suspect the instructions before the notes. Two rules already learned the hard way: a note whose purpose is to record a discrepancy is not committing it (a reconciliation digest produced six of the first run's seven), and a superseded document describing the old plan is correct rather than contradictory.

10. One commit carrying `state.json` + the run receipt + STATUS.md + `findings.md`, staged by explicit path, with the `Surface: code` trailer that CLAUDE.md's write-lanes section mandates. **This is the sweep-end commit, not the only commit this skill has to govern**: the same trailer and the same explicit-paths rule bind every finding append and amendment made between sweeps, per the ledger contract in § `.sweep/findings.md` is the durable memory. Reading this step as the whole commit rule is what let two untrailed finding commits land on 17 Aug 2026.

**Why both gates run twice.** At the gate they tell you whether your prior is trustworthy; at write-back they tell you whether what you just learned survived. The two failures this closes were both silent: the mirror stopped mirroring on 23 Jul and the ledger dropped a whole run's findings on 11 Aug, and in each case the run reported clean coverage while it happened. A number that cannot go red is decoration.

## Goal and audit runs (v3, added 12 Aug 2026, from the roadmap-corpus audit)

A goal run (a `/goal` invocation or an on-demand audit like the 12 Aug roadmap audit) is a sweep with a narrower question. Nine rules, each bought by a failure that night:

1. **Open with the full gate battery plus a cursor-delta row for EVERY surfaces.yaml entry**, even the ones the goal does not touch. Cheap readers for quiet surfaces. A surface the goal skips gets a SKIPPED row with the reason, never silence. The 12 Aug audit skipped comms surfaces by argument; the argument was right, but it lived in prose where nobody could check it.

2. **Agents read at the source, never from the prompt.** A prompt passes locators (sheet id, page id, ticket keys, file paths), never content. The one hand-transcribed doc id that night dropped one character and 404'd; the hand-condensed sheet dump was a second copy of the truth that existed only in a prompt. The standing reader for the roadmap is `tools/jove-drive/read-roadmap-grid.mjs`, which emits every cell with its embedded link targets and a grid hash.

3. **A finding is {claim, verbatim_quote, locator} or it is malformed.** After the find stage, a verify stage mechanically re-opens each locator and confirms the quote: `node tools/sweep/verify-quote.mjs` for files and grid JSON, a re-fetch for MCP artifacts. Unconfirmed findings are reported as PLAUSIBLE or dropped, never as fact.

4. **A completeness critic closes the run**: coverage per surface and per link class against surfaces.yaml and the goal manifest, as a table. Coverage is arithmetic, not narrative, same doctrine as the full sweep.

5. **Certification stamps.** At write-back the run records what it certified into `state.json` under `certified`: `{locator, version_or_hash, at, run_id}` per audited artifact (the sheet's grid hash, the PRD version, ticket updated-times). The next run diffs against certification and re-verifies only what moved; anything edited since certification is automatically a delta, which is how a concurrent hand edit surfaces without a guard having to catch it mid-write.

6. **Decision write-fanout.** Any decision taken during a session lists the artifacts that state it (sheet cell, ticket, PRD section, ledger claim) at decision time, and the run ends only when the fanout is complete or the gap is a named finding. Bought on 12 Aug: rank 4's cells said "PRD first" for hours after the same session had drafted, verified, ticketed and sent the copy. The place to write the fanout is the decision's `claims.json` entry.

7. **Workflow hardening.** The synthesis step asserts every agent returned non-null; a failed agent is retried once, then the run reports PARTIAL loudly in its return value. Results are read from the journal or output file, never from a truncated notification. Cached resume results can be empty; inspect before trusting.

8. **The goal manifest is the receipt's spine**: each goal clause mapped to its evidence or marked UNMET. "Goal complete" is a claim the receipt must prove, and one UNMET clause blocks it. Certifications (rule 5) and the coverage table (rule 4) are appendices to the manifest.

9. **Edits are proposed by agents, applied by the orchestrator through guarded writes** (content guards, read-back verification), and only where the case is obvious; anything else is a finding for Dhiraj. Writing is never delegated to a finder.

The named workflow implementing rules 2, 3, 4 and 7 for the roadmap sheet is `.claude/workflows/roadmap-audit.js`; trigger it by scriptPath from any session.

## Composition

Reuses `_shared/jove-connectors.md`, which carries the precedence table for the whole skill family (who reads what, who writes what, and who must not). It does not duplicate the general session sweep, which stays reactive and delta-based. If both would run, the session sweep handles the cross-work catch-up and this one handles the Labs deep rebuild.

Dependencies: Slack, Gmail, Calendar, Google Drive, Atlassian, tl;dv, Mixpanel and Linear authorized on whatever surface runs it. GitLab and Figma need OAuth and are commonly unavailable; both are declared in the registry with their reason, so their absence is reported rather than silently skipped.

## Attribution is a claim, and it gets verified (added 17 Aug 2026, after filing an action item on the wrong person)

**An action item is almost entirely attribution.** "Send the VP the lab details" is worthless without
the owner, and the owner is the part most likely to be wrong. Until today nothing in this skill
verified an owner, while quotes had a whole tool devoted to them.

**The incident.** In the 17 Aug the VP's Feedback call, Colleague-P asked for the VP's exact lab details
and Dhiraj said "I'll send that reply", then restated it as "my action point is to come back with the
exact details of the VP". Wispr's diarization on that call was scrambled and labelled both lines as
Colleague-P. Its auto-summary inherited the error, the sweep built its list from the summary, and
Dhiraj's own commitment landed on Colleague-P's list and off his. tl;dv had the correct labels the whole
time and was not consulted. The scramble had already been noticed and written down as a caveat, and
the caveat was never executed.

Four rules, and the fourth is the one that makes it structural rather than a reminder.

1. **Never take an owner from a generated summary.** Summaries derive owners from speaker labels; a
   broken label produces a confidently wrong owner with no visible defect. Owners come from a
   speaker-labelled transcript, always.
2. **Two surfaces means cross-check the owners.** Coverage is not interchangeable and neither is
   attribution. Where a meeting exists on more than one surface, compare the owners line by line
   before publishing any list. Disagreement is a finding, not a tie to be broken by preference.
3. **Self-address means the diarization is broken.** A speaker who addresses themselves by name, or
   who says "as X suggested" where X is themselves, is a mislabelled line. Do not repair that one
   line; discard the whole surface's attribution and re-derive from another. Both patterns are
   detected by `tools/meetings/attribution-check.mjs <transcript>`.
4. **The check runs, it is not remembered.** `node tools/meetings/attribution-check.mjs --index`
   audits `knowledge/meetings/surface-index.yaml` and exits non-zero on any unverified or
   summary-derived attribution. Run it before any run that publishes owners. A hand-written version
   of rule 3 already existed in the ledger on 17 Aug and was ignored by its own author within the
   hour, which is why this is now an exit code.

**Every meeting gets a surface-index entry**, recording which surfaces hold it, which one the owners
came from, whether that surface's diarization survived the self-address test, and whether two
surfaces were actually compared. Single-surface meetings are recorded as such: Design Standup exists
only on Gemini and Research PM sync only on Wispr, so for those the attribution can never be
cross-checked and the note must say so rather than implying confidence.

**Read every line of the transcript, and read the labels as data rather than fact.** Reading harder
would not have caught this one: the line genuinely said Colleague-P. What catches it is treating a
speaker label as a claim from a fallible system.

## The gate that makes the reading rules real (added 17 Aug 2026)

This skill has carried the Slack thread rules since 10 Aug and the DM fidelity rule since 17 Jul.
An audit on 17 Aug found the thread rules had reached **this skill and no other**, while three belt
routines read Slack daily with none of them. And this skill's own run that day summarised meetings
from platform summaries, contradicting `_shared/jove-connectors.md`, which had forbidden exactly
that in writing.

The conclusion is not that the rules need restating. It is that a rule nobody executes is not a rule.

**Before this run publishes any meeting summary, owner or action item:**

```bash
node tools/meetings/attribution-check.mjs --index
```

Non-zero exit blocks publication of owners. It enforces four things prose could not: the transcript
was read in full, we wrote our own summary rather than borrowing one, owners did not come from a
generated summary, and any meeting held on two or more surfaces had its owners cross-checked.

The canonical statement of both rule sets now lives in `_shared/jove-connectors.md` §§ "Reading a
call means reading the transcript" and "Slack: parents are not the channel", so every skill in the
family inherits one copy instead of drifting apart. Read them there; do not fork them here.


## Never report an item as open without looking at where it closes (gated 17 Aug 2026)

This routine names work as outstanding, so it can hand Dhiraj an item he already finished. That
happened five times on 17 Aug 2026, most sharply with his reply to the VP: sent 19:34 IST, listed as
his to send twenty minutes later. Every one had been checked against a meeting and against no
artifact.

- **Same-day, or it does not count.** A probe from this morning does not establish anything this
  evening. He acts between your checks.
- **The closing surface, not the originating one.** Email closes in the thread, Slack in the channel
  including replies, a ticket in Jira, a tracker item in the sheet row.
- **Searching is not reading.** Gmail `search_threads` truncates the per-thread message list, so a
  sent message can be missing from search and present in the thread; use `get_thread`. Same shape as
  `slack_read_channel` returning parents only. `open-item-check.mjs traps` lists the rest.

Gate, and it exits non-zero: `node tools/sweep/open-item-check.mjs check <the list you are about to
ship>`. Prose evidence is rejected; a probe must carry a real id, ts, row or status. This routine
runs unattended, which is why it carries the gate rather than a reminder: the Slack thread rule was
written into one skill on 10 Aug 2026 and an audit a week later found it had reached nowhere else.
