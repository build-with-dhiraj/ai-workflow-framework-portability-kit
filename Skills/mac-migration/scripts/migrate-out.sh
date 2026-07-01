#!/usr/bin/env bash
#
# migrate-out.sh — run on the OLD Mac to build a checksummed migration bundle.
#
# Produces, into a staging dir, one .tgz per project (regenerables excluded,
# .git + gitignored vaults/.lancedb INCLUDED), plus ~/.claude (stripped), ~/.agents,
# chat history, the Claude Desktop session store, dotfiles/secrets, a manifest.json
# (records the OLD username + project map so the restore isn't guessing), and
# CHECKSUMS.txt. Then upload the staging dir to cloud/external and VERIFY.
#
# Usage:  ./migrate-out.sh [--no-history]
#
set -uo pipefail

# ===========================================================================
# CONFIG — EDIT THIS BLOCK for your machine, then run.
# ===========================================================================
STAGE="$HOME/Desktop/mac-migration-out"      # where archives are written

# Projects to back up: "absolute-source-path|clean-name". The clean-name is what
# the folder becomes under ~/dev on the new Mac. Add one line per project.
PROJECTS=(
  # "$HOME/Connecting Dots|connecting-dots"
  # "$HOME/my-app|my-app"
)

# Non-code folders to archive to the NEW home root (not ~/dev) — handover dirs, etc.
HOME_LEVEL_DIRS=(
  # "$HOME/transition|transition"
)

# Extra dotfiles/dirs to include in the secrets/dotfiles archive (relative to $HOME).
DOTFILES=( .ssh .gitconfig .zshrc .zprofile .config )

# Regenerables excluded from every project archive.
EXCLUDES=( --exclude='*/node_modules' --exclude='*/.venv' --exclude='*/__pycache__'
           --exclude='*/.next' --exclude='*/dist' --exclude='*/build' --exclude='*/target'
           --exclude='.DS_Store' )
# ===========================================================================

WANT_HISTORY=1
[ "${1:-}" = "--no-history" ] && WANT_HISTORY=0

OLD_USER="$(whoami)"
OLD_HOME="$HOME"
log(){ echo "[migrate-out] $*"; }
mkdir -p "$STAGE"

if [ "${#PROJECTS[@]}" -eq 0 ] && [ "${#HOME_LEVEL_DIRS[@]}" -eq 0 ]; then
  log "WARNING: no PROJECTS/HOME_LEVEL_DIRS configured. Edit the CONFIG block first."
fi

# --- Project archives (exclude regenerables; include .git + gitignored data) ---
archive_project(){ # src | clean | destkind(dev|home)
  local src="$1" clean="$2"
  if [ ! -d "$src" ]; then log "SKIP (missing): $src"; return; fi
  log "archiving $src  ->  $clean.tgz"
  # --exclude of the repo's own worktrees dir (in-flight agent branches)
  tar "${EXCLUDES[@]}" --exclude="$(basename "$src")/.claude/worktrees" \
      -czf "$STAGE/$clean.tgz" -C "$(dirname "$src")" "$(basename "$src")"
}
for entry in "${PROJECTS[@]}";        do IFS='|' read -r s c <<<"$entry"; archive_project "$s" "$c"; done
for entry in "${HOME_LEVEL_DIRS[@]}"; do IFS='|' read -r s c <<<"$entry"; archive_project "$s" "$c"; done

# --- Claude config (stripped of transient/regenerable dirs; symlinks preserved) ---
if [ -d "$HOME/.claude" ]; then
  log "archiving ~/.claude -> claude-config.tgz (stripped)"
  tar --exclude='.claude/projects' --exclude='.claude/plugins/cache' --exclude='.claude/cache' \
      --exclude='.claude/shell-snapshots' --exclude='.claude/telemetry' --exclude='.claude/sessions' \
      --exclude='.claude/debug' --exclude='.claude/_backups' --exclude='.claude/backups' --exclude='.DS_Store' \
      -czf "$STAGE/claude-config.tgz" -C "$HOME" .claude $( [ -f "$HOME/.claude.json" ] && echo .claude.json )
fi

# --- ~/.agents (backs the symlinked skills — SKIPPING THIS BREAKS ~52 skills) ---
if [ -d "$HOME/.agents" ]; then
  log "archiving ~/.agents -> agents-skills-source.tgz (backs symlinked skills)"
  tar --exclude='.DS_Store' -czf "$STAGE/agents-skills-source.tgz" -C "$HOME" .agents
fi

# --- Chat history (~/.claude/projects) — large; skip with --no-history ---
if [ "$WANT_HISTORY" -eq 1 ] && [ -d "$HOME/.claude/projects" ]; then
  log "archiving ~/.claude/projects -> claude-history.tgz"
  tar -czf "$STAGE/claude-history.tgz" -C "$HOME" .claude/projects
fi

# --- Claude Desktop session store (its .json cwds get rewritten on restore) ---
CLA="$HOME/Library/Application Support/Claude"
if [ -d "$CLA" ]; then
  log "archiving Claude Desktop sessions -> claude-desktop-sessions.tgz"
  ( cd "$CLA" && tar -czf "$STAGE/claude-desktop-sessions.tgz" \
      $( ls -d local-agent-mode-sessions claude-code-sessions "Local Storage" "Session Storage" IndexedDB 2>/dev/null ) 2>/dev/null )
  [ -f "$CLA/claude_desktop_config.json" ] && cp "$CLA/claude_desktop_config.json" "$STAGE/"
fi

# --- Dotfiles / secrets (kept separate so they can be handled/deleted independently) ---
present=(); for d in "${DOTFILES[@]}"; do [ -e "$HOME/$d" ] && present+=("$d"); done
if [ "${#present[@]}" -gt 0 ]; then
  log "archiving dotfiles/secrets -> dotfiles-secrets.tgz  (${present[*]})"
  tar --exclude='.DS_Store' -czf "$STAGE/dotfiles-secrets.tgz" -C "$HOME" "${present[@]}"
fi

# --- manifest.json (the restore reads OLD_USER + the project map from this) ---
{
  echo "{"
  echo "  \"old_user\": \"$OLD_USER\","
  echo "  \"old_home\": \"$OLD_HOME\","
  echo "  \"projects\": ["
  first=1
  for entry in "${PROJECTS[@]}"; do IFS='|' read -r s c <<<"$entry"
    [ $first -eq 1 ] || echo ","; first=0
    printf '    {"old_basename": "%s", "clean": "%s", "dest": "dev"}' "$(basename "$s")" "$c"
  done
  for entry in "${HOME_LEVEL_DIRS[@]}"; do IFS='|' read -r s c <<<"$entry"
    [ $first -eq 1 ] || echo ","; first=0
    printf '    {"old_basename": "%s", "clean": "%s", "dest": "home"}' "$(basename "$s")" "$c"
  done
  echo ""; echo "  ],"
  echo "  \"secrets_not_backed_up\": [\"gh token (Keychain)\", \"MCP OAuth tokens (Keychain)\", \"per-service OAuth client keys\"]"
  echo "}"
} > "$STAGE/manifest.json"

# --- Checksums ---
log "writing CHECKSUMS.txt"
( cd "$STAGE" && shasum -a 256 $(ls | grep -v '^CHECKSUMS.txt$') > CHECKSUMS.txt )

# --- Copy this skill's restore scripts alongside the bundle ---
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SKILL_DIR/migrate-in.sh" "$SKILL_DIR/verify.sh" "$STAGE/" 2>/dev/null || true

echo
log "DONE. Bundle at: $STAGE"
log "Contents:"; ls -lh "$STAGE" | awk 'NR>1{print "   "$5"  "$9}'
cat <<EOF

NEXT (the pre-reset gate — do NOT wipe until all pass):
  1. Upload "$STAGE" to your cloud/external drive.
  2. VERIFY the round-trip: re-download one archive and run
       cd <downloaded-copy> && shasum -a 256 -c CHECKSUMS.txt   (every line must say OK)
  3. Confirm byte sizes on the cloud side match (not just "syncing").
  4. Write down: Apple ID, Google + 2FA, GitHub login, every MCP service login.
  5. If you can set the NEW Mac's short username = "$OLD_USER", do it — it deletes the path-rewrite phase.
  6. Keep a SECOND physical copy (external SSD / Time Machine) of the irreplaceable data.
EOF
