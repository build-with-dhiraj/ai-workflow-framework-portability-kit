# Code Audit — agentic-in/inferoa

- **Files read:** 254 text/source files (every line indexed)
- **Pushed at:** 2026-06-18T12:58:43Z
- **Stars:** 221

## Code-backed scores

- **direct_install:** 10
- **claude_code_native:** 7.5
- **loop_implementation:** 10
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 254
- **total:** 9.12

## Entrypoints (from code)

- skill_md: skills/coding-workflow/SKILL.md
- hooks: (none)
- loop_scripts: src/loop/automation.ts, src/loop/dashboard.ts, src/loop/discovery.ts, src/loop/evidence.ts, src/loop/git-verification.ts, src/loop/github-verification.ts, src/loop/health.ts, src/loop/http-verification.ts
- main_files: (none)

## Install facts (from manifests)

- bins: inferoa
- npm script `build`
- npm script `check`
- npm script `test`
- npm script `prepack`
- npm script `site:start`
- npm script `site:build`
- npm script `site:serve`
- npm script `experiment:long-horizon`
- npm script `validate:t0`
- npm script `validate:t1`
- npm script `validate:t2`
- npm script `validate:t3`

## Loop signals (line-indexed samples)

### stop_condition
- `website/blog/2026-06-08-announcing-inferoa.md:72` — | **Loop Engineering** | Design the objective, memory, feedback, verification, tools, and stop condition. | The agent ca
- `website/src/pages/index.tsx:8` — ["01", "Loop Engineering", "Design the objective, feedback, verifier, memory, tools, and stop condition instead of hand-
### verifier
- `.github/workflows/npm-publish.yml:97` — --verify-tag \
- `README.md:18` — Engineering**: give the model an objective, feedback, verification, memory, and tools,
- `README.md:33` — test, verify, decide, remember, and continue across loop tasks.
- `README.md:61` — verification, decisions, recovery, and completion evidence instead of stopping after the
- `README.md:82` — | Loop Engineering | [Loop Mode](https://github.com/agentic-in/inferoa) | Recursive long-horizon loops, loop tasks, atte
### hitl
- `src/cli.ts:21` — pauseLoopAutomationSchedule,
- `src/cli.ts:41` — pauseLoopDiscoverySchedule,
- `src/cli.ts:609` — case "pause":
- `src/cli.ts:610` — print(pauseLoopAutomationSchedule(app.store, requiredArg(rest, 0, "schedule")), options.json);
- `src/cli.ts:619` — throw new Error("Usage: inferoa automation list|add|run-due|pause|resume|remove ...");
### state_writeback
- `.github/workflows/npm-publish.yml:33` — registry-url: https://registry.npmjs.org
- `CONTRIBUTING.md:102` — ## Slash Command Registry
- `CONTRIBUTING.md:104` — The TUI slash command registry is the source of truth for in-product command
- `CONTRIBUTING.md:109` — - `src/tui/slash.ts` (registry and aliases)
- `docs/final-acceptance-task.md:127` — - session events, resources, prompt hashes, and endpoint evidence are persisted;
### loop_engine
- `README.md:32` — - **Loop Engineering**: `/loop` runs durable recursive loops that inspect, edit,
- `README.md:39` — <img src="website/static/gif/loop.gif" alt="Inferoa loop mode" width="860" />
- `README.md:60` — - **Loop/rubric driven work**: `/loop` carries an objective across loop tasks,
- `README.md:123` — /loop Improve this repository and prove it with tests.
- `README.md:147` — - `/loop` starts a recursive long-horizon loop: Inferoa keeps the objective,
### claude_native
- `.gitignore:4` — .claude/
- `src/loop/policy.ts:204` — expected_path: path.join(workspace.root, ".inferoa", "skills", skillId, "SKILL.md"),
- `src/model/providers.ts:149` — provider("claude-code", "Claude Code", "Claude Code OAuth session", "https://api.anthropic.com", "claude-sonnet-4-0", "a
- `src/model/providers.ts:153` — ], 31, { env: ["CLAUDE_CODE_OAUTH_TOKEN"] }),
- `src/model/providers.ts:447` — if (providerId === "claude-code") {

## README vs code

README claim: <p align="center">   <img src="assets/inferoa-logo.svg" alt="Inferoa" width="420" /> </p>  <p align="center">   <strong>Inference-native Tokenmaxxing Agent Harness for Loop Engineering</strong> </p>  <p align="center">   <a href="https://github.com/agentic-in/inferoa">GitHub</a>   ·   <a href="https

- Code contains loop engine / gate patterns (see loop signals above).
