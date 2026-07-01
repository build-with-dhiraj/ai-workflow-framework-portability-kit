# Lessons & pitfalls — the concentrated wisdom

Every trap this process actually hit, and the rule that prevents it. Read this
before driving a migration; it's the difference between "the script ran" and
"nothing was lost."

## Mental-model traps

- **"I'll sign into Claude and it'll sync."** No. Sign-in restores account/subscription only. Skills, agents, MCP, plugins, and chat history are local files. Say this out loud early.
- **"I'll just `git clone` my repos on the new Mac."** This silently drops gitignored vaults, `.lancedb` indexes, stashes, un-pushed commits, and any no-remote repo. **Extract the archive with `.git/` intact.** Clone only a repo you've verified is fully pushed and has zero gitignored data.
- **"The backup is done, I can wipe."** Not until you've re-downloaded one archive and checksum-verified it. Silent cloud corruption on a big upload is the quiet killer.
- **"Migration = it works now."** Migration = the irreplaceable data is redundant. One machine + a soon-to-be-deleted bundle is the original single point of failure.

## Identity / path-rewrite traps

- **Username is the whole ballgame.** If you can make the new short name equal the old one, the rewrite phase disappears — recommend it before setup.
- **`whoami` can lie during a rename.** The home dir may already be `/Users/NewName` while `whoami` still returns the old short name (short-name rename and home-move are separate operations). **Derive the rewrite target from `$HOME`**, not `whoami`.
- **A short-name rename is a real, separate step.** Renaming the *home folder* or the *full/display name* is NOT the same as the *account short name*. You can't rename the account you're logged into — it needs a second admin account + reboot, and on a managed/DEP Mac it should go through IT. Confirm `whoami == basename $HOME` afterward.
- **Two rewrite passes, in order:** (A) `/Users/old/ → /Users/new/`, then (B) relocate project roots (`/Users/new/Old Project → /Users/new/dev/clean-name`). Doing B before A misses matches.
- **Trailing-slash-only rules miss the bare form.** `s|/Users/old/|/Users/new/|g` will not touch `"/Users/old"` used as a whole value (a `.claude.json` project key, a plugin `projectPath`). Handle bare `/Users/old` explicitly.
- **Slugs aren't the paths.** Claude history dirs are `-Users-old-Project-…`; renaming must map both the user segment AND the relocated project root, and it must match the slugging rules (non-alphanumerics → `-`, but the **dot is kept** in e.g. `phy6.ai`).

## The "restore script only does config" trap

A restore script rewrites `~/.claude`, `.claude.json`, and per-repo `.git/config` — and leaves `/Users/old` in three breaking places:
1. **Project source code** (docs, `.env`, scripts) — a separate content rewrite (with backup + per-repo commit).
2. **Claude Desktop session `cwd`/`originCwd`/`worktreePath`** — the cause of **"Working directory no longer exists."** These are in the session `.json` metadata, not the config the script touches.
3. **History-slug ↔ session-cwd matching** — a chat loads history only if `slug(cwd)` equals its transcript dir. Repointing a session's `cwd` without matching the slug opens the chat **empty**. Fix by pointing cwd where the slug matches (symlink to real files if the folder moved, e.g. into `~/transition`), or renaming the transcript dir.
- **Restart Claude Desktop** after editing sessions — it caches cwds. And you can't ⌘Q it from inside a Desktop session; back up, edit the *other* sessions, restart at the end.

## Bundle-construction traps

- **The 52 symlinked skills point OUTSIDE `~/.claude`.** They're relative links into `~/.agents/skills/`. Archive `~/.agents` (`agents-skills-source.tgz`) or they restore as broken links. This is the single most important non-obvious catch.
- **Preserve symlinks as symlinks** in `claude-config.tgz` (don't dereference), so the above fix works.
- **Exclude regenerables, include gitignored data.** `node_modules/.venv/target/dist` out; `.git` + Obsidian vaults + `.lancedb` + stashes in. This can 2×+ shrink the bundle *and* is what makes it correct.
- **Hook packages referenced by `settings.json`** (e.g. a token-optimizer under `~/.claude`) must be in the archive, or every hook fails on the new Mac.
- **A repo with no remote is bundle-only.** Handover/eval repos often have no GitHub remote — the archive is the *only* copy of their history. Same for stashes.

## Verify-don't-assume traps

- **"Lost" secrets may not be lost.** OAuth keys, `.env`, and Azure/Sheets creds often ride *inside* a project archive (`repo/.secrets/`, `repo/.env`). Test the credential (make a real API call) before re-doing OAuth from scratch.
- **A newer cloud backup may contain nothing new.** Before merging a "newer" `claude-history.tgz`, diff it by transcript UUID and size — a re-tar can bump the timestamp/size with zero new chats, and blindly extracting it re-introduces stale `-Users-old-` slugs.
- **Documentation can be wrong.** A runbook line like "`npm i -g nlm` for NotebookLM" can point at the wrong package (that npm `nlm` is an unrelated Node tool; the real one is `go install github.com/tmc/nlm/...`). Verify install commands against reality.

## Resilience / security traps

- **A corporate/MDM (DEP-enrolled) Mac can be wiped by IT.** If you restore personal data + secrets onto a managed work machine, assume IT can inventory it and offboarding = wipe = loss. Keep the irreplaceable data backed up *off* that device.
- **Deleting the backup for security removes your only backup.** The bundle mixes data + secrets, and secrets are woven through the data archives — you can't cleanly delete "just the secrets." **Rotate** the exposed secrets (that neutralizes every copy) and keep the *data* archives as an off-device backup; or make an external-drive copy first.
- **Time Machine to an external SSD beats cloud** for a Mac move: it preserves Keychain (so most MCP logins survive), is a physical second copy, and lets Migration Assistant remap `/Users/old` automatically.
- **Fix the root cause:** replace hard-coded `/Users/old` paths in `~/.claude/settings.json` hooks with `$HOME`/`~` so the next move doesn't repeat all of this.

## The single best decisions, in order

1. Set the new account's short name = the old username (if you can) → no rewrites.
2. Extract archives, never clone → no silent data loss.
3. Checksum + verify round-trip before wiping → no corrupt-backup disaster.
4. Rewrite from `$HOME`, two passes, and don't forget code + session cwds → working chats.
5. Get a second physical copy + rotate secrets before deleting the bundle → real safety.
