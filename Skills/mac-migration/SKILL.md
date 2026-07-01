---
name: mac-migration
description: >-
  End-to-end playbook for moving a full developer + Claude Code environment from
  one Mac to another under the SAME Claude login — covers both the OLD-Mac backup
  side and the NEW-Mac restore side. Trigger this whenever the user is getting a
  new Mac/MacBook, replacing, selling, returning, or factory-resetting their
  current Mac, moving or syncing between two Macs, backing up their Claude setup
  (skills, agents, MCP servers, plugins, projects, chat history) before a wipe,
  restoring their environment on a fresh machine, or transferring code repos +
  Obsidian/RAG vaults + git stashes between Macs — even if they never say the word
  "migration" and even if they think signing into Claude will handle it. Signing
  into Claude restores only the account/subscription; it does NOT bring over the
  local ~/.claude state (skills, agents, MCP, history) or any project data, so
  this skill is almost always needed. Also use it when a restored chat throws
  "Working directory no longer exists" or skills/agents go missing after a move.
---

# Mac-to-Mac Migration (same Claude login)

## The one truth that changes everything

**Signing into Claude on the new Mac restores your account and subscription — nothing else.** Your skills, agents, MCP server definitions, plugins, chat history, and *all* project data are **local files** (mostly under `~/.claude`, `~/.agents`, and your code folders). If the old Mac is wiped before those are captured, they are gone. So this is not "zip and hope" — it is a deliberate **capture → verify → restore → reconcile** project.

Two facts shape the entire approach:
1. **The new Mac's username is usually different** (`pw` → `dhiraj`, `pranav`, etc.). Every absolute `/Users/<old>` path must be rewritten. If you can set the new account's short name to *match the old one*, you delete this entire problem — recommend it early.
2. **The two Macs are rarely online at once**, so Migration Assistant over the network often isn't an option. A checksummed archive bundle on cloud/external storage is the reliable path.

## Step 0 — figure out which side the user is on, and route

- **On the OLD Mac (still have it):** you are doing **Phase 1 — Prepare & Back Up**. Read `references/old-mac-prep.md` and drive `scripts/migrate-out.sh`. There may be a hard deadline (device return/reset) — establish it and work backward.
- **On the NEW Mac (old one gone/wiped):** you are doing **Phase 2 — Restore & Reconcile**. Read `references/new-mac-restore.md` and drive `scripts/migrate-in.sh`.
- **Debugging a half-done move** ("chats say working-directory-not-found", "my skills vanished"): jump to the reconciliation sections in `references/new-mac-restore.md` — this is almost always stale `/Users/<old>` paths in session metadata or broken skill symlinks.

Always confirm the old and new usernames (`whoami`, `echo $HOME`) before touching path-rewrite logic.

## The five non-negotiable doctrines

These are the hard-won lessons. Violate them and data is silently lost.

1. **Extract, never `git clone`.** Restore every project by *extracting its archive with `.git/` intact* — not by cloning from GitHub. Cloning gets the code but **silently drops gitignored data**: Obsidian/RAG vaults, `.lancedb` vector indexes, git **stashes**, un-pushed commits, and **repos with no remote at all**. Those exist *only* inside the archive. (Clone is a fallback only for a repo that is verified clean and fully pushed.)

2. **Username = everything.** Nearly all migration pain is absolute `/Users/<old>` paths. Derive the rewrite target from **`$HOME`, not `whoami`** (they can disagree during an account rename). Rewrite in two ordered passes: (A) `/Users/<old>/ → /Users/<new>/`, then (B) relocate project roots into their new home (e.g. `~/dev`). Then hunt the places a config-only rewrite misses (see doctrine 4).

3. **Verify, don't assume — in both directions.** Checksum the bundle and *re-download one archive to verify before wiping the old Mac* (silent cloud corruption on a multi-GB upload is a real risk). On the new Mac, don't trust "it ran" — grep for leftover `/Users/<old>`, find broken skill symlinks, count `.lancedb` dirs, and confirm chat history actually loads.

4. **A restore script rewrites *config*, not *everything*.** After the script runs, `/Users/<old>` typically survives in three places that break things and must be fixed separately: **(a) project source code**, **(b) bare `/Users/<old>` with no trailing slash**, and **(c) Claude Desktop session metadata** (the `cwd`/`originCwd`/`worktreePath` fields in `~/Library/Application Support/Claude/…-sessions/*.json`, plus the `~/.claude/projects/-Users-<old>-…` history slugs). Stale session `cwd`s cause **"Working directory no longer exists"**; and once those are fixed, a transcript filed under a slug that no longer matches its repaired `cwd` causes the distinct **"Session history unavailable"** (chat opens, but empty) — fixed by aligning the transcript to the cwd slug (`migrate-in.sh` step 7b).

5. **Done means redundant, not "it works."** A single Mac + a soon-to-be-deleted cloud bundle is the *same* single point of failure that motivated the migration — worse if it's a corporate/MDM-managed machine that IT can wipe. Before deleting the backup, make sure the irreplaceable data (vaults, `.lancedb`, no-remote repos, stashes) lives in a second place (external SSD / Time Machine). And replace hard-coded `/Users/<old>` paths in `~/.claude/settings.json` hooks with `$HOME`/`~` so the next move is painless.

## Phase 1 — OLD MAC: prepare & back up

Full detail + rationale in `references/old-mac-prep.md`. The arc:

1. **Set the deadline & keep awake.** If the Mac is being returned/reset, note the hard cutoff; run `caffeinate -dis &` so uploads don't stall.
2. **Harden — is Claude the only bridge?** Confirm nothing critical secretly depends on an editor/tool you're removing (check `~/.zshrc`/PATH, LaunchAgents/cron/git-hooks, `~/.claude.json` + MCP configs). Usually the tool you're worried about is "a leaf, not a hub" — the real risk is the reverse: the wipe destroys `~/.claude`, on-disk-only secrets, and un-pushed git work.
3. **Inventory what matters.** List the project folders to take (a Finder tag like Green is a good census signal). For each, separate **regenerable** (`node_modules`, `.venv`, `target`, `dist`) from **irreplaceable** (source, `.git`, gitignored vaults + `.lancedb`, stashes).
4. **Push code to remotes** where sensible (gives redundancy + sidesteps rewrites for code) — but this does NOT replace the archive for anything gitignored or no-remote.
5. **Build the bundle** with `scripts/migrate-out.sh` (parameterize your folders): one `.tgz` per project (regenerables excluded, `.git`+vaults included), plus `~/.claude` (stripped of caches), `~/.agents`, `~/.claude/projects` (history), the Claude Desktop session store, and dotfiles/secrets. **Critical catch:** the ~52 "symlinked" skills point *outside* `~/.claude` into `~/.agents/skills/` — archive `~/.agents` too or they restore as broken links.
6. **Checksum & verify round-trip.** Generate `CHECKSUMS.txt` (`shasum -a 256`); after upload, re-download one file and verify it matches.
7. **Write the runbook + a manifest** recording the old username, the project→destination map, and which secrets are intentionally *not* backed up (gh token, OAuth keys — they live in Keychain and get re-auth'd by hand).
8. **The gate — do NOT reset until:** the cloud shows the bundle fully uploaded (check byte sizes, not just "syncing"), and you've written down the credentials you'll re-enter (Apple ID, Google + 2FA, GitHub, each MCP login).

## Phase 2 — NEW MAC: restore & reconcile

Full detail in `references/new-mac-restore.md`. The arc:

1. **Sanity + identity.** `whoami`, `echo $HOME`, `df -h /` (need headroom). If the account name differs from the old one, decide now whether to rename it (cleanest) or proceed and rewrite paths. If an admin renames the short name, do it *before* the restore and confirm `whoami` matches the new `$HOME`.
2. **Prerequisites.** Homebrew, then `git gh node uv` (+ `rust`/`go` if your projects need them), the Obsidian app for vault re-add, and `gh auth login`.
3. **Get + verify the bundle** locally (force a full download off cloud stubs), then `shasum -a 256 -c CHECKSUMS.txt` — every line must say `OK`.
4. **Dry-run then run `scripts/migrate-in.sh`.** It verifies checksums, restores dotfiles/`~/.claude`/`~/.agents`/history/Desktop sessions, extracts projects into `~/dev`, rewrites paths (identity from `$HOME`), **rewrites Desktop session `cwd`s + history slugs**, and **aligns each chat transcript with its session's cwd slug (step 7b — so history actually loads)** — the gaps the naive script misses.
5. **Reconcile the completeness gaps** (doctrine 4) — the script bundled here handles them, but verify: no `/Users/<old>` in code/config, session `cwd`s all resolve, chats reopen with history.
6. **Per-repo deps + the india-invest-style exceptions**, re-add the Obsidian vaults in the app, re-auth MCP servers (the script prints the list).
7. **Verify** (doctrine 3) and **establish redundancy** (doctrine 5).

## Bundled resources

- `scripts/migrate-out.sh` — parameterized bundle builder (run on the OLD Mac). Reads a small config block (folders, home dir); excludes regenerables; includes `.git`+vaults; archives `~/.claude`/`~/.agents`/history/desktop-sessions/dotfiles; writes `CHECKSUMS.txt` and a `manifest.json` recording the old username + project map.
- `scripts/migrate-in.sh` — the restore script (run on the NEW Mac). `--dry-run` capable, idempotent, checksum-gated, `$HOME`-derived identity, pipefail-safe path rewriting, **includes the Desktop-config + session-`cwd` + history-slug rewrites, plus step 7b that aligns transcripts to their cwd slug ("Session history unavailable" fix)** and a broken-symlink verifier.
- `scripts/verify.sh` — post-restore verification (leftover paths, broken symlinks, `.lancedb` count, session-cwd resolution [4], misplaced-transcript count [4b], chat-history sanity).
- `references/old-mac-prep.md` — the full prepare-and-back-up methodology + rationale.
- `references/new-mac-restore.md` — the full restore + reconciliation methodology, including the session-`cwd`/slug fixes and the resilience audit.
- `references/lessons-and-pitfalls.md` — the concentrated wisdom: every trap this process hit and how to avoid it.

Read the relevant reference before driving its script. Confirm usernames and the folder list with the user before running anything destructive, and always `--dry-run` the restore first.
