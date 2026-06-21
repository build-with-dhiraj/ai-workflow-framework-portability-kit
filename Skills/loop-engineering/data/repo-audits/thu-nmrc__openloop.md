# Code Audit — thu-nmrc/openloop

- **Files read:** 32 text/source files (every line indexed)
- **Pushed at:** 2026-06-10T04:08:27Z
- **Stars:** 56

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 0.0
- **loop_implementation:** 10
- **registry_memory:** 1.0
- **verification:** 8.0
- **file_coverage:** 32
- **total:** 3.85

## Entrypoints (from code)

- skill_md: (none)
- hooks: (none)
- loop_scripts: src/openloop/__init__.py, src/openloop/__main__.py, src/openloop/cli.py, src/openloop/config.py, src/openloop/reporting.py, src/openloop/runner.py, src/openloop/timeutil.py, src/openloop/workspace.py
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### stop_condition
- `README.md:73` — openloop run .openloop/demo --max-rounds 1
- `README.md:158` — openloop run WORKSPACE [--max-rounds N]
- `VISION.md:7` — A timer that repeats a prompt is not enough. A real loop has sensors, state, actuators, evaluators, and stop conditions.
- `src/openloop/cli.py:58` — return runner.run(max_rounds=args.max_rounds)
- `src/openloop/cli.py:95` — p_run.add_argument("--max-rounds", type=int, default=None, help="override config total_rounds")
### verifier
- `CONTRIBUTING.md:19` — - Prefer deterministic verification over self-evaluation.
- `README.md:7` — <p align="center"><b>Agent-agnostic loop engineering for projects that must be played with, tested, repaired, verified, 
- `README.md:16` — > A loop is not a timer. A real loop knows the current process, PID, log path, step, speed, ETA, verifier result, baseli
- `README.md:18` — OpenLoop is a small Python toolkit and prompt pack for building **monitored feedback loops around any software agent**. 
- `README.md:29` — | Agent claims success too early | ❌ Self-review | ✅ External `verify` and optional `baseline` gates |
### hitl
- `src/openloop/workspace.py:44` — """# Loop Contract\n\nOpenLoop runs a monitored feedback cycle:\n\n1. Confirm the true active process, PID, log path, cu
### state_writeback
- `README.md:52` — Persist heartbeat, progress, logs, artifacts
- `src/openloop/workspace.py:44` — """# Loop Contract\n\nOpenLoop runs a monitored feedback cycle:\n\n1. Confirm the true active process, PID, log path, cu

## README vs code

README claim: <p align="center">   <img src="assets/openloop-logo.png" alt="openloop logo" width="820"/> </p>  <h1 align="center">openloop</h1>  <p align="center"><b>Agent-agnostic loop engineering for projects that must be played with, tested, repaired, verified, and improved until they are actually healthy.</b>

- Code contains loop engine / gate patterns (see loop signals above).
