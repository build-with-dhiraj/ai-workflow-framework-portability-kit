# Code Audit — WAPA0012/cc-loop-engineering

- **Files read:** 16 text/source files (every line indexed)
- **Pushed at:** 2026-06-21T05:54:49Z
- **Stars:** 0

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 1.2
- **loop_implementation:** 8.4
- **registry_memory:** 0.0
- **verification:** 10
- **file_coverage:** 16
- **total:** 3.84

## Entrypoints (from code)

- skill_md: (none)
- hooks: (none)
- loop_scripts: engine/loop.sh
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### stop_condition
- `README.md:59` — - `--rounds N` — override max rounds
- `engine/loop.sh:11` — #   MAX_ROUNDS       — 最大循环轮次（默认 20）
- `engine/loop.sh:37` — --rounds)  MAX_ROUNDS="$2"; shift 2 ;;
- `engine/loop.sh:53` — MAX_ROUNDS="${MAX_ROUNDS:-20}"
- `engine/loop.sh:103` — log "  上限: $MAX_ROUNDS 轮"
### verifier
- `README.md:9` — A single worker handles the entire task — understanding the project, making decisions, executing changes, and verifying 
- `README.md:25` — → critic (find issues, mandatory search)
- `README.md:27` — → reviewer (assess change impact)
- `README.md:30` — gate (mechanical verification)
- `README.md:41` — | Independent review | none (self-review) | yes (critic/reviewer) |
### hitl
- `README.md:61` — ## Human-in-the-Loop (Pause / Intervene)
- `README.md:63` — Users can intervene at any time by creating signal files:
- `README.md:67` — touch state/stop_signal
- `README.md:70` — echo "Focus on edge cases in _checkDup" > state/pause_signal
- `README.md:73` — - `stop_signal`: stops after the current round, runs final verification
### loop_engine
- `README.md:48` — bash engine/loop.sh scenarios/ai-memory-solo.conf
- `README.md:51` — bash engine/loop.sh scenarios/ai-memory-fix.conf --mode team
- `README.md:151` — │   ├── loop.sh           # Main entry (loop driver + solo/team branching + gate)
- `engine/loop.sh:2` — # loop.sh — CC-Loop 循环引擎主入口
- `engine/loop.sh:3` — # 用法: bash loop.sh <任务配置文件>
### claude_native
- `.gitignore:6` — .claude/
- `README.md:106` — Configure `~/.claude/settings.json`:
- `README.md:115` — "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "1000000",
- `README.md:123` — - Docs: https://docs.bigmodel.cn → Claude Code

## README vs code

README claim: # CC-Loop — Autonomous Coding Loop Engine  An autonomous loop engine that drives projects toward goals. Two modes: a single worker (solo, default) or multi-agent collaboration (team).  ## Two Modes  ### Solo Mode (Default)  A single worker handles the entire task — understanding the project, making 

- Code contains loop engine / gate patterns (see loop signals above).
