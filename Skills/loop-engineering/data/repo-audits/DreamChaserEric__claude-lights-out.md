# Code Audit — DreamChaserEric/claude-lights-out

- **Files read:** 21 text/source files (every line indexed)
- **Pushed at:** 2026-06-10T13:12:42Z
- **Stars:** 10

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 4.2
- **loop_implementation:** 0.0
- **registry_memory:** 2.5
- **verification:** 7.5
- **file_coverage:** 21
- **total:** 2.34

## Entrypoints (from code)

- skill_md: (none)
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### stop_condition
- `lightsout-workflow.js:149` — const MAX_ROUNDS = 5
- `lightsout-workflow.js:208` — while (!approved && round < MAX_ROUNDS) {
- `lightsout-workflow.js:234` — } else if (round >= MAX_ROUNDS) {
- `lightsout-workflow.js:235` — log(`${phaseName}: proceeding after ${MAX_ROUNDS} rounds`)
- `lightsout-workflow.js:315` — while (!testsPassed && testRound < MAX_ROUNDS) {
### verifier
- `README-zh.md:52` — C --> S1[Spec Writer ↔ Reviewer]
- `README-zh.md:53` — S1 --> S2[UX Designer ↔ Reviewer]
- `README-zh.md:54` — S2 --> S3[Architect ↔ Reviewer]
- `README-zh.md:59` — S7 --> S8[E2E Verification]
- `README-zh.md:124` — + reviewer/fixer prompts
### state_writeback
- `README.md:9` — A fully automated development pipeline for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Agents write, 
- `README.md:89` — - **Docs are ground truth** — `spec.md`, `design.md`, `architecture.md` persist across sessions
- `install.sh:26` — echo "  /lightsout Build a REST API with Express and Postgres"
- `prompts/architect.md:50` — | Database | {e.g., PostgreSQL} | {16} | {why} |
- `prompts/visual-qa.md:72` — - **State persistence:** Refresh page, verify data survives (if applicable)
### claude_native
- `README-zh.md:9` — 基于 [Claude Code dynamic workflow](https://docs.anthropic.com/en/docs/claude-code) 的全自动开发流水线。Agent 在循环中编写、审查、测试、修复——交付可运行
- `README-zh.md:30` — 需要：[Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)（支持 workflow 功能）。
- `README-zh.md:113` — 编辑 `~/.claude/lights-out/prompts/` 下的任何 prompt：
- `README-zh.md:129` — - 需要 Claude Code 且支持 workflow
- `README.md:9` — A fully automated development pipeline for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Agents write, 

## README vs code

README claim: # claude-lights-out  [English](README.md) | [中文](README-zh.md)  **Structured engineering loops, not one-shot vibes.**  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)  A fully automated development pipeline for [Claude Code](https://docs.anthropic.com/en/docs/claude-cod

- Loop implementation in code is thin or documentation-only.
