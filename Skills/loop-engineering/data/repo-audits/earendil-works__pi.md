# Code Audit — earendil-works/pi

- **Files read:** 843 text/source files (every line indexed)
- **Pushed at:** 2026-06-20T20:27:39Z
- **Stars:** 64325

## Code-backed scores

- **direct_install:** 10
- **claude_code_native:** 10
- **loop_implementation:** 10
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 843
- **total:** 9.62

## Entrypoints (from code)

- skill_md: packages/coding-agent/examples/extensions/dynamic-resources/SKILL.md, packages/coding-agent/test/fixtures/skills/consecutive-hyphens/SKILL.md, packages/coding-agent/test/fixtures/skills/disable-model-invocation/SKILL.md, packages/coding-agent/test/fixtures/skills/invalid-name-chars/SKILL.md, packages/coding-agent/test/fixtures/skills/invalid-yaml/SKILL.md, packages/coding-agent/test/fixtures/skills/long-name/SKILL.md, packages/coding-agent/test/fixtures/skills/missing-description/SKILL.md, packages/coding-agent/test/fixtures/skills/multiline-description/SKILL.md
- hooks: (none)
- loop_scripts: packages/agent/src/agent-loop.ts, packages/agent/test/agent-loop.test.ts, packages/coding-agent/test/sdk-codex-cache-probe-tool-loop.ts
- main_files: (none)

## Install facts (from manifests)

- bins: pi-ai, pi
- npm script `clean`
- npm script `build`
- npm script `check`
- npm script `check:browser-smoke`
- npm script `check:pinned-deps`
- npm script `check:shrinkwrap`
- npm script `check:ts-imports`
- npm script `profile:tui`
- npm script `profile:rpc`
- npm script `test`
- npm script `version:patch`
- npm script `version:minor`

## Loop signals (line-indexed samples)

### stop_condition
- `packages/coding-agent/CHANGELOG.md:622` — - Fixed interactive sessions to exit when terminal input is lost instead of continuing in a broken state.
- `packages/coding-agent/CHANGELOG.md:4601` — - Fixed terminal corruption after exit when shell integration sequences (OSC 133) appeared in bash output. These sequenc
- `packages/coding-agent/src/core/keybindings.ts:67` — "app.exit": { defaultKeys: "ctrl+d", description: "Exit when editor is empty" },
### verifier
- `.github/workflows/build-binaries.yml:127` — - name: Verify release artifacts are committed
- `.github/workflows/npm-audit.yml:30` — - name: Verify registry signatures
- `.pi/prompts/cl.md:27` — - Verify a changelog entry exists in the affected package(s)
- `.pi/prompts/cl.md:28` — - For external contributions (PRs), verify format: `Description ([#N](url) by [@user](url))`
- `.pi/prompts/is.md:14` — 3. Do not trust analysis written in the issue. Independently verify behavior and derive your own analysis from the code 
### hitl
- `packages/ai/src/providers/anthropic.ts:1241` — case "pause_turn": // Stop is good enough -> resubmit
- `packages/coding-agent/examples/extensions/custom-provider-anthropic/index.ts:322` — case "pause_turn":
- `packages/coding-agent/examples/extensions/doom-overlay/README.md:29` — | Pause/Quit | Q |
- `packages/coding-agent/examples/extensions/doom-overlay/doom-component.ts:61` — // Unpause if resuming
- `packages/coding-agent/examples/extensions/doom-overlay/doom-component.ts:63` — this.engine.pushKey(true, DoomKeys.KEY_PAUSE);
### state_writeback
- `.github/workflows/build-binaries.yml:33` — persist-credentials: false
- `.github/workflows/build-binaries.yml:44` — registry-url: 'https://registry.npmjs.org'
- `.github/workflows/build-binaries.yml:100` — persist-credentials: false
- `.github/workflows/build-binaries.yml:106` — registry-url: 'https://registry.npmjs.org'
- `.github/workflows/npm-audit.yml:30` — - name: Verify registry signatures
### loop_engine
- `packages/agent/CHANGELOG.md:106` — - Added `shouldStopAfterTurn` to the low-level agent loop config for gracefully exiting after a completed turn before po
- `packages/agent/CHANGELOG.md:255` — - Added `beforeToolCall` and `afterToolCall` hooks to `AgentOptions` and `AgentLoopConfig` for preflight blocking and po
- `packages/agent/CHANGELOG.md:259` — - Added configurable tool execution mode to `Agent` and `agentLoop` via `toolExecution: "parallel" | "sequential"`, with
- `packages/agent/CHANGELOG.md:297` — - Added `transport` to `AgentOptions` and `AgentLoopConfig` forwarding, allowing stream transport preference (`"sse"`, `
- `packages/agent/CHANGELOG.md:477` — - **AgentLoopConfig callbacks renamed**: `getQueuedMessages` split into `getSteeringMessages` and `getFollowUpMessages`.
### claude_native
- `.gitignore:19` — .claude/
- `packages/agent/src/harness/skills.ts:46` — * Traverses directories recursively, loads `SKILL.md` files, loads direct root `.md` files as skills, honors ignore file
- `packages/agent/src/harness/skills.ts:138` — if (entry.name !== "SKILL.md") continue;
- `packages/agent/src/harness/system-prompt.ts:10` — "When a skill file references a relative path, resolve it against the skill directory (parent of SKILL.md / dirname of t
- `packages/agent/src/harness/types.ts:41` — * Skill loaded from a `SKILL.md` file or provided by an application.

## README vs code

README claim: <p align="center">   <a href="https://pi.dev">     <img alt="pi logo" src="https://pi.dev/logo-auto.svg" width="128">   </a> </p> <p align="center">   <a href="https://discord.com/invite/3cU7Bz4UPx"><img alt="Discord" src="https://img.shields.io/badge/discord-community-5865F2?style=flat-square&logo=

- Code contains loop engine / gate patterns (see loop signals above).
