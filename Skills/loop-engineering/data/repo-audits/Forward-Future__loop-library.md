# Code Audit — Forward-Future/loop-library

- **Files read:** 80 text/source files (every line indexed)
- **Pushed at:** 2026-06-21T03:22:46Z
- **Stars:** 483

## Code-backed scores

- **direct_install:** 2.0
- **claude_code_native:** 7.5
- **loop_implementation:** 10
- **registry_memory:** 7.5
- **verification:** 7.5
- **file_coverage:** 80
- **total:** 6.75

## Entrypoints (from code)

- skill_md: skills/loop-library/SKILL.md
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)

- npm script `check`
- npm script `deploy`
- npm script `dev`
- npm script `test`

## Loop signals (line-indexed samples)

### stop_condition
- `audits/seo-geo-2026-06-19.md:30` — stop condition.
- `audits/seo-geo-2026-06-19.md:59` — answer, explicit stop condition, visible citations to the
- `scripts/check.mjs:235` — ["goal-forge-loop", ["SPEC.md", "GOAL.md", "done_when"]],
- `scripts/loop-data.mjs:123` — "Define what satisfactory means before starting, such as module boundaries, dependency direction, passing tests, and acc
- `scripts/loop-data.mjs:943` — "Promote only a meaningful, regression-free holdout win; log every result and return the champion at the stop condition.
### verifier
- `.github/workflows/ci.yml:17` — verify:
- `.github/workflows/ci.yml:18` — name: Verify
- `.github/workflows/ci.yml:36` — - name: Verify generated artifacts
- `AGENTS.md:12` — verification criteria, and related-loop links.
- `AGENTS.md:125` — - Hold the lock through here.now finalize and production verification.
### state_writeback
- `scripts/loop-data.mjs:784` — "Persist state across rounds and finish with the verdict, remaining findings, checks, and pull-request link.",
- `scripts/loop-data.mjs:787` — "Clodex separates the Claude builder from the Codex reviewer and turns review feedback into a bounded repair loop. Persi
- `scripts/loop-data.mjs:985` — "Separating critic and builder roles makes disagreement explicit. A persistent objection log prevents circular debate, w
- `site/catalog.json:916` — "Persist state across rounds and finish with the verdict, remaining findings, checks, and pull-request link."
- `site/catalog.json:918` — "why": "Clodex separates the Claude builder from the Codex reviewer and turns review feedback into a bounded repair loop
### loop_engine
- `.github/workflows/ci.yml:53` — node --check scripts/loop-data.mjs
- `AGENTS.md:5` — - Treat `scripts/loop-data.mjs` as the canonical SEO/GEO content catalog for
- `AGENTS.md:22` — `scripts/loop-data.mjs`; the social-image builder refuses to replace a path
- `AGENTS.md:36` — node --check scripts/loop-data.mjs
- `AGENTS.md:77` — `https://loop-library-forms.mberman84.workers.dev`. Configure it from a clean
### claude_native
- `README.md:88` — | Claude Code | `npx skills add Forward-Future/loop-library --skill loop-library --agent claude-code -g -y` |
- `README.md:97` — --agent claude-code \
- `README.md:128` — - **Claude Code:** type `/loop-library` followed by your request.
- `README.md:146` — For example, in Claude Code or Cursor:
- `audits/seo-geo-2026-06-19.md:60` — [Claude Agent SDK loop documentation](https://code.claude.com/docs/en/agent-sdk/agent-loop)

## README vs code

README claim: # Loop Library  The Loop Library skill is an installable guide for your AI agent. Tell it what you want to get done and it can find a published loop, audit and repair an existing one, adapt one to your situation, or help you design a new one through a short conversation.  Loop Library is a collectio

- Code contains loop engine / gate patterns (see loop signals above).
