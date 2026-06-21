# Code Audit — Dryxio/auto-re-agent

- **Files read:** 92 text/source files (every line indexed)
- **Pushed at:** 2026-04-10T07:12:55Z
- **Stars:** 326

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 0.3
- **loop_implementation:** 8.8
- **registry_memory:** 5.0
- **verification:** 7.5
- **file_coverage:** 92
- **total:** 4.13

## Entrypoints (from code)

- skill_md: (none)
- hooks: (none)
- loop_scripts: src/re_agent/agents/loop.py, tests/test_agents/test_loop.py
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### stop_condition
- `src/re_agent/agents/loop.py:1` — """Fix loop — reverser -> checker -> fix, bounded by max rounds."""
- `src/re_agent/agents/loop.py:30` — max_rounds: int = 4,
- `src/re_agent/agents/loop.py:41` — """Run the reverser->checker->fix loop up to max_rounds.
- `src/re_agent/agents/loop.py:48` — max_rounds: Maximum fix iterations
- `src/re_agent/agents/loop.py:75` — for round_num in range(1, max_rounds + 1):
### verifier
- `README.md:3` — Autonomous reverse-engineering agent — source-aware reverser/checker loop, objective verifier, parity engine, and Ghidra
- `README.md:9` — re-agent automates a reverse-engineering workflow by combining a reverser/checker loop with Ghidra decompilation through
- `README.md:21` — │   ├── Agent Loop (reverser → checker → fix, max N rounds)
- `README.md:25` — │   ├── Objective Verifier (call-count + control-flow sanity checks)
- `README.md:27` — │   ├── Parity Engine (GREEN/YELLOW/RED verification gate)
### state_writeback
- `src/re_agent/cli/cmd_parity.py:70` — from re_agent.backend.registry import create_backend
- `src/re_agent/cli/cmd_reverse.py:25` — from re_agent.backend.registry import create_backend
- `src/re_agent/cli/cmd_reverse.py:27` — from re_agent.llm.registry import create_provider
- `src/re_agent/core/models.py:212` — # Hook registry
- `src/re_agent/core/models.py:217` — """A single hook from the hooks CSV registry."""
### loop_engine
- `README.md:21` — │   ├── Agent Loop (reverser → checker → fix, max N rounds)
- `docs/architecture.md:6` — CLI -> Config -> Orchestrator -> Agent Loop -> LLM Providers
- `src/re_agent/backend/stub.py:27` — Useful for testing the agent loop, prompt construction, and
- `src/re_agent/orchestrator/single.py:28` — """Reverse a single function: agent loop -> optional parity check -> record.
- `src/re_agent/parity/source_indexer.py:306` — while True:
### claude_native
- `src/re_agent/llm/registry.py:22` — from re_agent.llm.claude import ClaudeProvider

## README vs code

README claim: # re-agent  Autonomous reverse-engineering agent — source-aware reverser/checker loop, objective verifier, parity engine, and Ghidra backend.  ## Overview  Demo: [YouTube](https://youtu.be/zBQJYMKmwAs?si=emi1kDsJ81-2-tc3)  re-agent automates a reverse-engineering workflow by combining a reverser/che

- Code contains loop engine / gate patterns (see loop signals above).
