#!/usr/bin/env bash
#
# verify.sh — post-restore verification on the NEW Mac.
# Usage:  ./verify.sh [old-username]     (old username read from a nearby manifest.json if omitted)
#
set -uo pipefail
have(){ command -v "$1" >/dev/null 2>&1; }
INTERP=""; have python3 && INTERP=python3; [ -z "$INTERP" ] && have node && INTERP=node

OLD="${1:-}"
if [ -z "$OLD" ]; then
  for m in "$HOME/Downloads"/*/manifest.json "$(dirname "${BASH_SOURCE[0]}")/../manifest.json" "$(dirname "${BASH_SOURCE[0]}")/manifest.json"; do
    [ -f "$m" ] && OLD="$(sed -nE 's/.*"old_user"[: ]*"([^"]+)".*/\1/p' "$m" | head -1)" && [ -n "$OLD" ] && break
  done
fi
[ -z "$OLD" ] && OLD="pw"
CLA="$HOME/Library/Application Support/Claude"
echo "=== verifying restore (old user: $OLD, new home: $HOME) ==="

echo "[1] leftover /Users/$OLD in CONFIG + CODE (excl chat/session logs):"
n=$(grep -rlI "/Users/$OLD/" "$HOME/.claude" "$HOME/.claude.json" "$HOME/dev" 2>/dev/null | grep -vE '/projects/|\.jsonl$|/tasks/|/history' | wc -l | tr -d ' ')
echo "    $n files  $( [ "$n" = 0 ] && echo '✅ clean' || echo '⚠️ rewrite these (code/config)' )"

echo "[2] broken skill symlinks (want 0 — confirms ~/.agents restored):"
b=$(find "$HOME/.claude/skills" -maxdepth 1 -type l ! -exec test -e {}/SKILL.md \; -print 2>/dev/null | wc -l | tr -d ' ')
echo "    $b  $( [ "$b" = 0 ] && echo '✅' || echo '⚠️' )"

echo "[3] Obsidian/RAG .lancedb indexes present under ~/dev:"
echo "    $(find "$HOME/dev" -name '.lancedb' -type d 2>/dev/null | wc -l | tr -d ' ') found"

echo "[4] Desktop session cwds pointing at a MISSING dir (want 0 — else 'working directory no longer exists'):"
if [ -n "$INTERP" ] && [ "$INTERP" = python3 ]; then
  python3 - "$CLA/claude-code-sessions" "$CLA/local-agent-mode-sessions" <<'PY'
import json,os,sys
bad=0
for base in sys.argv[1:]:
  if not os.path.isdir(base): continue
  for root,_,files in os.walk(base):
    for fn in files:
      if not fn.endswith(".json"): continue
      try: j=json.load(open(os.path.join(root,fn)))
      except: continue
      for k in ("cwd","originCwd","worktreePath"):
        v=j.get(k)
        if isinstance(v,str) and v.startswith("/Users/") and not os.path.isdir(v): bad+=1
print(f"    {bad}  " + ("✅" if bad==0 else "⚠️ run migrate-in.sh session repair / see references/new-mac-restore.md §5c"))
PY
else
  echo "    (needs python3 for a precise check) — grep for /Users/$OLD in session .json:"
  echo "    $(grep -rhoE '"(cwd|originCwd|worktreePath)":"/Users/'"$OLD"'' "$CLA" --include='*.json' 2>/dev/null | wc -l | tr -d ' ') stale refs in session metadata"
fi

echo "[5] chat history present:"
echo "    $(find "$HOME/.claude/projects" -name '*.jsonl' 2>/dev/null | wc -l | tr -d ' ') transcripts"

echo "[6] fragile hard-coded paths in settings.json hooks (should be \$HOME/~, not /Users/...):"
echo "    $(grep -c "/Users/" "$HOME/.claude/settings.json" 2>/dev/null || echo 0) hard-coded /Users refs  (replace with \$HOME to future-proof)"

echo "[7] irreplaceable git state (confirm it survived — these exist ONLY locally):"
for d in "$HOME"/dev/*; do [ -d "$d/.git" ] || continue
  st=$(git -C "$d" stash list 2>/dev/null | wc -l | tr -d ' '); rem=$(git -C "$d" remote 2>/dev/null | head -1)
  [ "$st" -gt 0 ] 2>/dev/null && echo "    $(basename "$d"): $st stash(es)"
  [ -z "$rem" ] && echo "    $(basename "$d"): NO REMOTE (archive is the only copy — back it up off-device)"
done
echo
echo "Reminder: restart Claude Desktop to apply session edits; get a 2nd off-device copy before deleting the bundle."
