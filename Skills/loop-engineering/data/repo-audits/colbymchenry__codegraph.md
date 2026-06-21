# Code Audit — colbymchenry/codegraph

- **Files read:** 326 text/source files (every line indexed)
- **Pushed at:** 2026-06-21T06:42:31Z
- **Stars:** 52393

## Code-backed scores

- **direct_install:** 10
- **claude_code_native:** 10
- **loop_implementation:** 4.800000000000001
- **registry_memory:** 7.5
- **verification:** 9.5
- **file_coverage:** 326
- **total:** 8.25

## Entrypoints (from code)

- skill_md: .claude/skills/add-lang/SKILL.md, .claude/skills/agent-eval/SKILL.md
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)

- bins: codegraph
- npm script `build`
- npm script `preuninstall`
- npm script `copy-assets`
- npm script `dev`
- npm script `cli`
- npm script `test`
- npm script `test:watch`
- npm script `test:eval`
- npm script `eval`
- npm script `clean`
- npm script `start`
- npm script `preview`

## Loop signals (line-indexed samples)

### stop_condition
- `docs/design/mixed-ios-and-react-native-bridging.md:544` — Phase 1 (Swift↔ObjC) is done when:
### verifier
- `.claude/skills/add-lang/SKILL.md:31` — - [ ] 5. Build + verify-extraction loop until PASS
- `.claude/skills/add-lang/SKILL.md:127` — ### Step 5 — Build + verify loop
- `.claude/skills/add-lang/SKILL.md:135` — node scripts/add-lang/verify-extraction.mjs <sample-repo> <lang>
- `.claude/skills/add-lang/SKILL.md:137` — `verify-extraction.mjs` fails (exit 1) if the language isn't detected or only
- `.claude/skills/add-lang/SKILL.md:140` — mappings in `<lang>.ts`, `npm run build`, re-index, re-verify. **Repeat until
### hitl
- `docs/design/dynamic-dispatch-coverage-playbook.md:270` — | JS × Swift/Kotlin | Expo Modules | JS `requireNativeModule('X').fn(...)` → Swift/Kotlin `Function("fn") { ... }` | R (
- `docs/design/mixed-ios-and-react-native-bridging.md:417` — | swift-objc | `init`, `description`, `hash`, `isEqual`, `copy`, `count`, `value`, `data`, `string`, `object`, `add`, `r
- `docs/design/mixed-ios-and-react-native-bridging.md:456` — | **expo-camera** | 72 | 41 (Swift + Kotlin; covers `takePictureAsync`, `record`, `resumePreview`, `getAvailableLenses`,
- `src/resolution/frameworks/swift-objc.ts:103` — 'pause',
### state_writeback
- `.claude/skills/agent-eval/corpus.json:332` — "question": "How does a Swift `Realm.write { realm.add(obj) }` reach the Objective-C persistence layer?"
- `.github/workflows/release.yml:48` — registry-url: https://registry.npmjs.org
- `.github/workflows/release.yml:163` — # Skip any already on the registry so a re-run only fills in gaps.
- `.github/workflows/release.yml:174` — - name: Verify every package is actually on the registry
- `.github/workflows/release.yml:177` — # npm publish can print success without persisting; confirm against the
### loop_engine
- `__tests__/liveness-watchdog.test.ts:95` — 'setTimeout(() => { while (true) {} }, 150);',
- `__tests__/liveness-watchdog.test.ts:106` — 'const k=[]; for (let i=0;i<40;i++) k.push(Buffer.alloc(1024*1024,i)); global.__k=k; setTimeout(() => { while (true) {} 
- `__tests__/security.test.ts:583` — // Create a symlink from src/loop -> tempDir (parent directory)
- `src/graph/traversal.ts:629` — while (true) {
- `src/mcp/liveness-watchdog.ts:7` — * regex, an accidental `while (true)` — wedges the event loop, and from JS you
### claude_native
- `.claude/skills/add-lang/SKILL.md:166` — `.claude/skills/agent-eval/corpus.json` (fields: `name`, `repo`, `size`,
- `.claude/skills/agent-eval/SKILL.md:35` — **Step 2 — language.** Read `.claude/skills/agent-eval/corpus.json`. Ask with
- `.gitignore:41` — .claude/settings.local.json
- `.gitignore:42` — .claude/scheduled_tasks.lock
- `.gitignore:43` — .claude/handoffs/

## README vs code

README claim: <div align="center">  # CodeGraph  ## 🎉 1.0 Released!  Already installed? Run `codegraph upgrade` to update in place.  Follow [@getcodegraph](https://x.com/getcodegraph) on X for updates.  ### Supercharge Claude Code, Cursor, Codex, OpenCode, Hermes Agent, Gemini, Antigravity, and Kiro with Semantic

- Code contains loop engine / gate patterns (see loop signals above).
