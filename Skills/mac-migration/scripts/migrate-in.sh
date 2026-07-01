#!/usr/bin/env bash
#
# migrate-in.sh — run on the NEW Mac to restore a bundle built by migrate-out.sh.
#
# Restores dotfiles + ~/.claude + ~/.agents + chat history + Claude Desktop sessions,
# extracts projects into ~/dev, and rewrites every /Users/<old> path to the new home —
# INCLUDING the Claude Desktop config, the Desktop session cwds, and the history slugs
# (the places a naive restore misses and that cause "Working directory no longer exists"
# and empty-history chats).
#
# CRITICAL: restore projects by EXTRACTING their .tgz — never `git clone`. The archives
# are the only source of gitignored vaults, .lancedb indexes, stashes, and no-remote repos.
#
# Usage:  ./migrate-in.sh [bundle-dir] [--dry-run] [--yes]
#
set -uo pipefail

DRY=0; YES=0; BUNDLE=""
for a in "$@"; do case "$a" in
  --dry-run) DRY=1;; --yes|-y) YES=1;;
  -*) echo "unknown flag: $a" >&2; exit 2;;
  *) BUNDLE="$a";;
esac; done
[ -z "$BUNDLE" ] && BUNDLE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log(){ echo "[migrate-in] $*"; }
warn(){ echo "[migrate-in] WARN: $*" >&2; }
run(){ if [ "$DRY" -eq 1 ]; then echo "  DRY: $*"; else "$@"; fi; }
have(){ command -v "$1" >/dev/null 2>&1; }
INTERP=""; have python3 && INTERP=python3; [ -z "$INTERP" ] && have node && INTERP=node

HOME_DIR="$HOME"
NEW_USER="$(basename "$HOME_DIR")"   # <-- identity from $HOME, NOT whoami (they disagree during a rename)
NEW_HOME="$HOME_DIR"
DEV="$HOME_DIR/dev"
CLA="$HOME_DIR/Library/Application Support/Claude"
DESKTOP_CFG="$CLA/claude_desktop_config.json"

# ---- Old username: from manifest.json (preferred) or --------------------------
OLD_USER=""
if [ -f "$BUNDLE/manifest.json" ]; then
  OLD_USER="$(sed -nE 's/.*"old_user"[: ]*"([^"]+)".*/\1/p' "$BUNDLE/manifest.json" | head -1)"
fi
[ -z "$OLD_USER" ] && OLD_USER="pw"   # last-resort default; override below if wrong
log "Old user (from bundle): $OLD_USER    New user (from \$HOME): $NEW_USER"
OLD_HOME="/Users/$OLD_USER"

if [ "$OLD_USER" = "$NEW_USER" ]; then
  log "Old == new username: paths already match, no rewrite needed (restore only)."
fi
if [ "$YES" -eq 0 ] && [ "$DRY" -eq 0 ]; then
  printf "Restore into %s, rewriting %s -> %s ? [y/N/override-old-user] " "$HOME_DIR" "$OLD_HOME" "$NEW_HOME"
  read -r r; case "$r" in y|Y|yes) :;; ""|n|N) echo "aborted"; exit 1;; *) OLD_USER="$r"; OLD_HOME="/Users/$OLD_USER";; esac
fi

# ---- 1. Checksum gate ---------------------------------------------------------
if [ -f "$BUNDLE/CHECKSUMS.txt" ]; then
  log "verifying checksums (abort on mismatch)"
  if [ "$DRY" -eq 0 ]; then ( cd "$BUNDLE" && shasum -a 256 -c CHECKSUMS.txt ) || { echo "CHECKSUM MISMATCH — re-download the bundle."; exit 1; }; fi
else warn "no CHECKSUMS.txt — proceeding WITHOUT integrity check"; fi

# ---- 2. Dotfiles / secrets ----------------------------------------------------
[ -f "$BUNDLE/dotfiles-secrets.tgz" ] && { log "restore dotfiles"; run tar -xzf "$BUNDLE/dotfiles-secrets.tgz" -C "$HOME_DIR"; }
[ -d "$HOME_DIR/.ssh" ] && { run chmod 700 "$HOME_DIR/.ssh"; [ -f "$HOME_DIR/.ssh/id_ed25519" ] && run chmod 600 "$HOME_DIR/.ssh/id_ed25519"; }

# ---- 3. Claude state ----------------------------------------------------------
[ -f "$BUNDLE/claude-config.tgz" ]        && { log "restore ~/.claude";      run tar -xzf "$BUNDLE/claude-config.tgz" -C "$HOME_DIR"; }
[ -f "$BUNDLE/agents-skills-source.tgz" ] && { log "restore ~/.agents (backs symlinked skills)"; run tar -xzf "$BUNDLE/agents-skills-source.tgz" -C "$HOME_DIR"; }
[ -f "$BUNDLE/claude-history.tgz" ]       && { log "restore chat history";   run tar -xzf "$BUNDLE/claude-history.tgz" -C "$HOME_DIR"; }
if [ -f "$BUNDLE/claude-desktop-sessions.tgz" ]; then log "restore Desktop sessions"; run mkdir -p "$CLA"; run tar -xzf "$BUNDLE/claude-desktop-sessions.tgz" -C "$CLA"; fi
[ -f "$BUNDLE/claude_desktop_config.json" ] && { run mkdir -p "$CLA"; run cp "$BUNDLE/claude_desktop_config.json" "$DESKTOP_CFG"; }

# ---- 4. Extract projects into ~/dev (or ~ for home-dest) — EXTRACT, never clone ----
run mkdir -p "$DEV"
declare -a MAP_OLD=() MAP_NEW=()      # old-basename -> new-abs-root (for later relocation)
add_map(){ MAP_OLD+=("$1"); MAP_NEW+=("$2"); }
extract_one(){ # tgz-basename | clean | dest(dev|home)
  local base="$1" clean="$2" dest="$3" arc="$BUNDLE/$base.tgz"
  [ -f "$arc" ] || { warn "archive missing: $arc"; return; }
  local into="$DEV"; [ "$dest" = home ] && into="$HOME_DIR"
  log "extract $base.tgz -> $into/"
  run tar -xzf "$arc" -C "$into"
  # the archive's top-level dir may differ from clean; rename if needed
  if [ "$DRY" -eq 0 ]; then
    local top; top="$(tar -tzf "$arc" 2>/dev/null | head -1 | cut -d/ -f1)"
    if [ -n "$top" ] && [ "$top" != "$clean" ] && [ -d "$into/$top" ] && [ ! -e "$into/$clean" ]; then mv "$into/$top" "$into/$clean"; fi
    add_map "$top" "$into/$clean"; add_map "$clean" "$into/$clean"
  fi
}
if [ -f "$BUNDLE/manifest.json" ] && [ -n "$INTERP" ]; then
  # read project rows from manifest via python3/node
  while IFS='|' read -r base clean dest; do [ -n "$base" ] && extract_one "$base" "$clean" "$dest"; done < <(
    if [ "$INTERP" = python3 ]; then python3 -c 'import json,sys;[print(f"{p[\"old_basename\"]}|{p[\"clean\"]}|{p[\"dest\"]}") for p in json.load(open(sys.argv[1]))["projects"]]' "$BUNDLE/manifest.json";
    else node -e 'JSON.parse(require("fs").readFileSync(process.argv[1])).projects.forEach(p=>console.log(`${p.old_basename}|${p.clean}|${p.dest}`))' "$BUNDLE/manifest.json"; fi )
else
  warn "no manifest/interpreter: extracting every *.tgz that looks like a project (no clean-rename)"
  for arc in "$BUNDLE"/*.tgz; do b="$(basename "$arc" .tgz)"; case "$b" in claude-config|claude-history|claude-desktop-sessions|agents-skills-source|dotfiles-secrets|home-*|documents|slack-*) continue;; esac; extract_one "$b" "$b" dev; done
fi

# ---- 5. Path rewrite — pipefail-safe, two passes, incl Desktop config + bare form ----
rewrite_tree(){ # file-or-dir
  local t="$1"; [ -e "$t" ] || return 0
  # (A) generic user rename  (|| true so a no-match grep can't abort under pipefail)
  { grep -rlI "$OLD_HOME/" "$t" 2>/dev/null || true; } | while IFS= read -r f; do [ -n "$f" ] || continue
    [ "$DRY" -eq 1 ] && { echo "  DRY (A) $f"; continue; }; sed -i '' "s|$OLD_HOME/|$NEW_HOME/|g" "$f"; done
  # (A-bare) whole-value "/Users/old" with no trailing slash (quotes/EOL boundaries)
  { grep -rlI "\"$OLD_HOME\"" "$t" 2>/dev/null || true; } | while IFS= read -r f; do [ -n "$f" ] || continue
    [ "$DRY" -eq 1 ] && { echo "  DRY (bare) $f"; continue; }; sed -i '' "s|\"$OLD_HOME\"|\"$NEW_HOME\"|g" "$f"; done
  # (B) relocate project roots into their new home
  local i; for i in "${!MAP_OLD[@]}"; do
    local needle="$NEW_HOME/${MAP_OLD[$i]}" repl="${MAP_NEW[$i]}"
    { grep -rlI "$needle" "$t" 2>/dev/null || true; } | while IFS= read -r f; do [ -n "$f" ] || continue
      [ "$DRY" -eq 1 ] && { echo "  DRY (B) $f"; continue; }; sed -i '' "s|$needle|$repl|g" "$f"; done
  done
}
log "rewriting paths ($OLD_HOME -> $NEW_HOME) across ~/.claude, .claude.json, Desktop config, sessions, per-repo config"
rewrite_tree "$HOME_DIR/.claude"
rewrite_tree "$HOME_DIR/.claude.json"
rewrite_tree "$DESKTOP_CFG"
rewrite_tree "$CLA/claude-code-sessions"
rewrite_tree "$CLA/local-agent-mode-sessions"
for i in "${!MAP_NEW[@]}"; do rewrite_tree "${MAP_NEW[$i]}/.git/config"; rewrite_tree "${MAP_NEW[$i]}/.claude"; done

# ---- 6. Rename Claude history slugs  -Users-OLD-...  ->  -Users-NEW-... --------
PROJDIR="$HOME_DIR/.claude/projects"
if [ -d "$PROJDIR" ] && [ "$DRY" -eq 0 ]; then
  log "renaming history slugs -Users-$OLD_USER- -> -Users-$NEW_USER-"
  for d in "$PROJDIR"/-Users-"$OLD_USER"*; do [ -e "$d" ] || continue
    bn="$(basename "$d")"; rest="${bn#-Users-$OLD_USER}"; nb="-Users-$NEW_USER$rest"
    [ "$bn" = "$nb" ] && continue; [ -e "$PROJDIR/$nb" ] || mv "$d" "$PROJDIR/$nb"; done
fi

# ---- 7. Repair Desktop session cwds that point at a MISSING dir (the big fix) ---
# After the sed rewrite, some cwds still don't exist (deleted worktrees, never-restored
# folders). Collapse each to its nearest EXISTING ancestor (fallback $HOME) so no chat
# throws "Working directory no longer exists". Generic — no project-specific knowledge.
if [ -n "$INTERP" ] && [ "$DRY" -eq 0 ]; then
  log "repairing session cwds (collapse missing dirs to nearest existing ancestor)"
  SC='
import json,os,sys
H=os.path.expanduser("~")
def fix(p):
  if not isinstance(p,str) or not p.startswith("/Users/"): return p
  q=p
  while q and not os.path.isdir(q): q=os.path.dirname(q)
  return q or H
n=0
for root,_,files in os.walk(sys.argv[1]):
  for fn in files:
    if not fn.endswith(".json"): continue
    fp=os.path.join(root,fn)
    try: j=json.load(open(fp))
    except Exception: continue
    ch=False
    for k in ("cwd","originCwd","worktreePath"):
      v=j.get(k)
      if isinstance(v,str) and v.startswith("/Users/") and not os.path.isdir(v):
        nv=fix(v)
        if nv!=v: j[k]=nv; ch=True
    if ch:
      json.dump(j,open(fp,"w")); n+=1
print("  sessions repaired:",n)
'
  if [ "$INTERP" = python3 ]; then
    python3 -c "$SC" "$CLA/claude-code-sessions" 2>/dev/null
    python3 -c "$SC" "$CLA/local-agent-mode-sessions" 2>/dev/null
  else
    warn "python3 not found; skipping cwd-collapse. Run verify.sh and see references/new-mac-restore.md §5(c)."
  fi
else [ "$DRY" -eq 0 ] && warn "no python3/node: skipping session-cwd repair (see references/new-mac-restore.md §5c)"; fi

# ---- 7b. Align chat transcripts with session cwds (fix "session history unavailable") ----
# A chat loads history only if slug(session.cwd) matches the dir holding its <id>.jsonl,
# where slug turns every char except [A-Za-z0-9.] into '-'. After the cwd repairs above,
# some transcripts sit under a DIFFERENT slug (pruned-worktree slugs, the old bare-user
# slug, underscore/paren folders) -> the folder is valid but history won't load. Copy each
# transcript into the slug matching its (valid) cwd. Additive — never deletes.
if [ "$INTERP" = python3 ] && [ "$DRY" -eq 0 ]; then
  log "aligning chat transcripts with session cwds (fix 'session history unavailable')"
  python3 - "$CLA/claude-code-sessions" "$CLA/local-agent-mode-sessions" "$HOME_DIR/.claude/projects" <<'PY'
import json,os,glob,shutil,sys
sess=sys.argv[1:3]; PROJ=sys.argv[3]
def slug(p): return "".join(c if (c.isalnum() or c==".") else "-" for c in p)
tindex={}
for d in glob.glob(f"{PROJ}/*"):
  if os.path.isdir(d):
    for fn in os.listdir(d):
      if fn.endswith(".jsonl"): tindex.setdefault(fn[:-6],[]).append(d)
def recs(o):
  if isinstance(o,dict):
    if isinstance(o.get("cwd"),str): yield o
    for v in o.values(): yield from recs(v)
  elif isinstance(o,list):
    for v in o: yield from recs(v)
seen=set(); n=0
for base in sess:
  if not os.path.isdir(base): continue
  for root,_,files in os.walk(base):
    for fn in files:
      if not fn.endswith(".json"): continue
      try: j=json.load(open(os.path.join(root,fn)))
      except Exception: continue
      for r in recs(j):
        for sid in [i for i in (r.get("cliSessionId"),r.get("sessionId")) if i]:
          if sid in seen: continue
          seen.add(sid); dst=f"{PROJ}/{slug(r['cwd'])}"
          if os.path.exists(f"{dst}/{sid}.jsonl"): break
          srcs=[d for d in tindex.get(sid,[]) if os.path.exists(f"{d}/{sid}.jsonl")]
          if not srcs: break
          os.makedirs(dst,exist_ok=True)
          shutil.copy2(f"{srcs[0]}/{sid}.jsonl", f"{dst}/{sid}.jsonl")
          if os.path.isdir(f"{srcs[0]}/{sid}"): shutil.copytree(f"{srcs[0]}/{sid}", f"{dst}/{sid}", dirs_exist_ok=True)
          n+=1; break
print("  transcripts aligned to cwd slug:",n)
PY
fi

# ---- 8. Worktree prune ---------------------------------------------------------
for i in "${!MAP_NEW[@]}"; do d="${MAP_NEW[$i]}"; [ -d "$d/.git" ] && run git -C "$d" worktree prune 2>/dev/null; done

# ---- 8b. Background launchd agents ("Allow in the Background") — stage + rewrite, DON'T auto-load ----
# launchd program paths are LITERAL (no $HOME/env expansion), so the plists must be path-rewritten
# like code; and macOS BLOCKS each agent until it is approved in System Settings. We stage them to a
# REVIEW dir and rewrite paths, but never auto-activate (that needs your OK + a GUI toggle).
if [ -f "$BUNDLE/launchagents.tgz" ]; then
  LA_REVIEW="$HOME_DIR/mac-migration-launchagents-review"
  log "staging background launchd agents -> $LA_REVIEW (review; NOT auto-loaded)"
  run mkdir -p "$LA_REVIEW"
  run tar -xzf "$BUNDLE/launchagents.tgz" -C "$LA_REVIEW"     # -> $LA_REVIEW/Library/LaunchAgents/*.plist
  rewrite_tree "$LA_REVIEW"                                    # same (A) user + (B) project-root rewrite
  if [ "$DRY" -eq 0 ]; then cat <<EOF
  Staged (path-rewritten) at: $LA_REVIEW/Library/LaunchAgents/   inventory: $BUNDLE/launchagents-inventory.txt
  These are macOS "Allow in the Background" agents — NOT auto-installed (they need your OK + a GUI toggle).
  Restore ONLY your own agents (skip app-managed ones — Google/Chrome/OpenAI updaters etc. reappear on reinstall):
    1. Ensure the script it runs exists + is executable (chmod +x); create its StandardOut/ErrorPath log dirs.
    2. cp "$LA_REVIEW/Library/LaunchAgents/<label>.plist" ~/Library/LaunchAgents/
    3. grep -R "/Users/$OLD_USER" ~/Library/LaunchAgents      # must be EMPTY
    4. launchctl bootstrap gui/\$(id -u) ~/Library/LaunchAgents/<label>.plist   # fallback: launchctl load -w
       launchctl enable gui/\$(id -u)/<label> ; launchctl kickstart -k gui/\$(id -u)/<label>   # for always-on
    5. System Settings > General > Login Items & Extensions > "Allow in the Background" > toggle each ON (required).
    6. Verify: launchctl list | grep <label> ; tail its log for crash-loops.
EOF
  fi
fi

# ---- 9. Broken-symlink check + MCP checklist ----------------------------------
if [ "$DRY" -eq 0 ] && [ -d "$HOME_DIR/.claude/skills" ]; then
  broken="$(find "$HOME_DIR/.claude/skills" -maxdepth 1 -type l ! -exec test -e {}/SKILL.md \; -print 2>/dev/null)"
  [ -n "$broken" ] && warn "broken skill symlinks (is ~/.agents restored?):" && printf '  %s\n' $broken || log "skills OK: no broken symlinks"
fi
echo; log "MCP servers to re-authenticate (only definitions travel; re-auth each):"
if [ -n "$INTERP" ]; then
  for cfg in "$HOME_DIR/.claude.json" "$HOME_DIR/.claude/mcp.json" "$DESKTOP_CFG"; do [ -f "$cfg" ] || continue
    if [ "$INTERP" = python3 ]; then python3 -c 'import json,sys
def c(o):
  if isinstance(o,dict):
    if isinstance(o.get("mcpServers"),dict):
      for k in o["mcpServers"]: print("  [ ]",k)
    [c(v) for v in o.values()]
  elif isinstance(o,list): [c(v) for v in o]
try: c(json.load(open(sys.argv[1])))
except: pass' "$cfg"; fi; done | sort -u
fi

cat <<EOF

RESTORE COMPLETE.$( [ "$DRY" -eq 1 ] && echo "  (dry run — nothing changed)" )
Next:
  - Per-repo deps (npm install / uv sync / cargo build …) — regenerables were excluded.
  - Re-add Obsidian vaults in the app ("Open folder as vault"); folders + .lancedb are already on disk.
  - Re-auth the MCP servers listed above.
  - Run verify.sh, then RESTART Claude Desktop (it caches session cwds).
  - Make a SECOND copy of the irreplaceable data before deleting the bundle (see references/lessons-and-pitfalls.md).
EOF
