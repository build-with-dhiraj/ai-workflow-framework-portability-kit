# Code Audit — bhavinkotak/agentforge

- **Files read:** 205 text/source files (every line indexed)
- **Pushed at:** 2026-06-16T09:20:55Z
- **Stars:** 0

## Code-backed scores

- **direct_install:** 2.0
- **claude_code_native:** 3.9
- **loop_implementation:** 1.6
- **registry_memory:** 7.5
- **verification:** 8.0
- **file_coverage:** 205
- **total:** 4.0

## Entrypoints (from code)

- skill_md: (none)
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)

- npm script `dev`
- npm script `build`
- npm script `preview`
- npm script `lint`

## Loop signals (line-indexed samples)

### stop_condition
- `docs/PRD.md:389` — - Conversation stop condition check (did the agent stop too early or loop?).
- `web/src/pages/RunDetailPage.tsx:208` — max_iterations: '🏁 Max rounds reached',
### verifier
- `.github/workflows/action-test.yml:27` — # Verify required top-level fields are present
- `.github/workflows/agent-test-nvidia.yml:56` — # Use a free NVIDIA NIM model for both agent and judge.
- `.github/workflows/agent-test-nvidia.yml:57` — # Override via AGENTFORGE_JUDGE_MODEL env if needed.
- `.github/workflows/agent-test-nvidia.yml:64` — # Override via AGENTFORGE_JUDGE_MODEL to try other free models.
- `.github/workflows/agent-test-nvidia.yml:65` — AGENTFORGE_JUDGE_MODEL: mistralai/mistral-small-4-119b-2603
### hitl
- `docs/PRD.md:12` — AgentForge is a self-improving AI agent optimization platform. The sole required input is an **agent file** — a declarat
### state_writeback
- `.github/workflows/agent-test-nvidia.yml:43` — ~/.cargo/registry/index/
- `.github/workflows/agent-test-nvidia.yml:44` — ~/.cargo/registry/cache/
- `.github/workflows/ci.yml:55` — ~/.cargo/registry/index/
- `.github/workflows/ci.yml:56` — ~/.cargo/registry/cache/
- `.github/workflows/ci.yml:71` — postgres:
### loop_engine
- `crates/agentforge-runner/src/runner.rs:1118` — // Always return a tool call so the agent loops
- `web/src/components/ScorecardDisplay.tsx:36` — looping: 'Agent Looping',
### claude_native
- `README.md:373` — # Bedrock model for agent runs (defaults to anthropic.claude-3-haiku-20240307-v1:0)
- `README.md:374` — AGENTFORGE_BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0
- `README.md:381` — | Claude 3.5 Sonnet v2 | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
- `README.md:382` — | Claude 3.5 Haiku | `anthropic.claude-3-5-haiku-20241022-v1:0` |
- `README.md:383` — | Claude 3 Haiku | `anthropic.claude-3-haiku-20240307-v1:0` |

## README vs code

README claim: # AgentForge  > **One file in. A better agent out.**  [![CI](https://github.com/bhavinkotak/agentforge/actions/workflows/ci.yml/badge.svg)](https://github.com/bhavinkotak/agentforge/actions/workflows/ci.yml) [![Release](https://img.shields.io/github/v/release/bhavinkotak/agentforge?sort=semver)](htt

- Loop implementation in code is thin or documentation-only.
