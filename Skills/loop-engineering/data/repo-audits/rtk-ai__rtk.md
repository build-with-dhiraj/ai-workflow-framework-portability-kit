# Code Audit — rtk-ai/rtk

- **Files read:** 365 text/source files (every line indexed)
- **Pushed at:** 2026-06-20T15:24:24Z
- **Stars:** 64297

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 10
- **loop_implementation:** 0.0
- **registry_memory:** 7.5
- **verification:** 8.0
- **file_coverage:** 365
- **total:** 4.33

## Entrypoints (from code)

- skill_md: .claude/skills/code-simplifier/SKILL.md, .claude/skills/design-patterns/SKILL.md, .claude/skills/issue-triage/SKILL.md, .claude/skills/performance/SKILL.md, .claude/skills/pr-review/SKILL.md, .claude/skills/pr-triage/SKILL.md, .claude/skills/repo-recap/SKILL.md, .claude/skills/rtk-tdd/SKILL.md
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### verifier
- `.claude/agents/code-reviewer.md:2` — name: code-reviewer
- `.claude/agents/code-reviewer.md:3` — description: Use this agent when you need comprehensive code quality assurance, security vulnerability detection, or per
- `.claude/agents/code-reviewer.md:24` — → src/hooks/ (init, rewrite, verify, trust)
- `.claude/agents/code-reviewer.md:37` — 2. **Call-site analysis**: Trace ALL callers of modified functions, list every input variant, verify each has a test
- `.claude/agents/code-reviewer.md:39` — 4. **Token savings**: Verify savings claim is tested with real fixture
### hitl
- `src/cmds/go/go_cmd.rs:393` — _ => {} // run, pause, cont, etc.
### state_writeback
- `.claude/agents/code-reviewer.md:19` — → src/core/tracking.rs (SQLite, token metrics)
- `.claude/agents/rust-rtk.md:312` — - `src/core/tracking.rs` - SQLite token savings tracking (`rtk gain`)
- `.claude/agents/system-architect.md:44` — │   ├── tracking.rs       ← SQLite, token metrics, 90-day retention
- `.claude/commands/tech/audit-codebase.md:189` — Grep "serde_json\|regex\|rusqlite" Cargo.toml
- `.claude/commands/tech/codereview.md:64` — | `src/core/tracking.rs`         | SQLite patterns + DB path config           |
### claude_native
- `.claude/agents/code-reviewer.md:3` — description: Use this agent when you need comprehensive code quality assurance, security vulnerability detection, or per
- `.claude/agents/rtk-testing-specialist.md:234` — - **Hook integration changes**: Verify Claude Code hook rewriting works
- `.claude/agents/rust-rtk.md:350` — rtk discover                       # Analyze Claude Code history for missed opportunities
- `.claude/agents/technical-writer.md:15` — - Hook integration documentation for Claude Code
- `.claude/agents/technical-writer.md:25` — - **Hook Integration**: Claude Code integration, command routing, configuration

## README vs code

README claim: <p align="center">   <img src="https://avatars.githubusercontent.com/u/258253854?v=4" alt="RTK - Rust Token Killer" width="500"> </p>  <p align="center">   <strong>High-performance CLI proxy that reduces LLM token consumption by 60-90%</strong> </p>  <p align="center">   <a href="https://github.com/

- Loop implementation in code is thin or documentation-only.
