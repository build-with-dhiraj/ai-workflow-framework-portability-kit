# Code Audit — ordinary9843/gitizens

- **Files read:** 125 text/source files (every line indexed)
- **Pushed at:** 2026-06-21T06:01:08Z
- **Stars:** 5

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 6.9
- **loop_implementation:** 2.4000000000000004
- **registry_memory:** 1.0
- **verification:** 3.5
- **file_coverage:** 125
- **total:** 2.66

## Entrypoints (from code)

- skill_md: .claude/skills/git/SKILL.md
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### verifier
- `.claude/hooks/session-start:10` — - .claude/rules/testing.md     three-step verification per change
- `.claude/rules/change-surface.md:3` — Every non-trivial change to this repo touches multiple layers. Before declaring work complete, verify each affected laye
- `.claude/rules/testing.md:1` — # Testing and Verification
- `.claude/skills/git/examples/test.md:10` — test: verify event expiry handles no active event
- `tests/test_events.py:379` — """Verify the 15% probability gate is the sole logic in fire_random_event."""
### state_writeback
- `tests/test_citizens.py:143` — def test_achievements_persist_in_json(self, tmp_path, monkeypatch):
- `tests/test_proposals.py:311` — # Garbage date string in caller -> function falls back to today and persists it.
### loop_engine
- `docs/index.html:1259` — const walkerAlpha = w.alpha !== undefined ? w.alpha : 1;
- `docs/index.html:1269` — ctx.globalAlpha = 0.2 * walkerAlpha;
- `docs/index.html:1272` — ctx.globalAlpha = walkerAlpha;
### claude_native
- `.claude/commands/git.md:14` — Full convention, type table, examples, and rules live in `.claude/skills/git/SKILL.md`. Read that file and follow the wo
- `.claude/hooks/session-start:2` — # session-start: inject pointer to canonical project rules into Claude Code session.
- `.claude/hooks/session-start:3` — # Keep this hook minimal — canonical content lives in CLAUDE.md and .claude/rules/.
- `.claude/hooks/session-start:10` — - .claude/rules/testing.md     three-step verification per change
- `.claude/hooks/session-start:11` — - .claude/rules/python.md      source-code language and emoji rules

## README vs code

README claim: <div align="center">   <img src="docs/logo.png" alt="Gitizens" width="160" /> </div>  ---  ## What is Gitizens?  [![Tests](https://github.com/ordinary9843/gitizens/actions/workflows/test.yml/badge.svg)](https://github.com/ordinary9843/gitizens/actions/workflows/test.yml) ![Coverage](docs/coverage-ba

- Loop implementation in code is thin or documentation-only.
