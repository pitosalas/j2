# Current Working Context — 2026-02-20

## What was just completed

- Fixed runner `fill_template` to single-pass regex (stopped placeholder expansion inside substituted content)
- Renamed `/spec-review` → `/refresh` throughout; deleted stale command file
- Updated `gen_features.md` and `gen_tasks.md` templates to be idempotent (preserve status on re-run)
- Updated FOOTER format to require integer `<N>` counts with explicit reminder
- Implemented F21 `/next`: reads `next:` from state.md, delegates to appropriate runner command
- Added functional tests: `/refresh` render, `/task-next` render, install.sh (3 tests), F21 resolver, F22 ANSI footer
- Marked F04, F11, F18, F21, F22 as done

## What is currently in progress

Nothing in progress. Next High-priority not-started feature is **F20** (Prompt-with-Default).

## What is next

1. `/task-next` — will land on F20 (task file exists at `.j2/tasks/F20.md`)
2. After F20: Medium-priority F10 (`/milestone`), F16 (`/checkpoint`), F17 (`/try`), F19 (`/deploy`) — templates exist, need functional tests

## Open questions

- **Spec not updated**: `.j2/specs/j2.md` still has old runner path and `prompt.md` reference. Update with revised spec from last `/refresh`.
- **F20 scope**: Prompt-with-default is aspirational — current commands take args inline. Decide: implement in templates or leave as-is.

## Feature Status

| Feature | Priority | Status | Tests |
|---|---|---|---|
| F01 Directory Scaffold | High | done | ✅ |
| F02 YAML Config | High | done | ✅ |
| F03 Template System | High | done | ✅ |
| F04 /refresh | High | done | ✅ |
| F05 /features-gen | High | done | ✅ |
| F06 /features-refine | High | done | ✅ |
| F07 /tasks-gen | High | done | ✅ |
| F08 /tasks-refine | High | done | ✅ |
| F09 /task-start | High | done | ✅ |
| F10 /milestone | Medium | not started | ❌ |
| F11 install.sh | Medium | done | ✅ |
| F12 Slash Commands | High | done | ✅ |
| F13 File State | High | done | ✅ |
| F14 ROS2 Profile | Low | not started | ❌ |
| F15 Rules File | High | done | ✅ |
| F16 /checkpoint | Medium | not started | ❌ |
| F17 /try | Medium | not started | ❌ |
| F18 /task-next | High | done | ✅ |
| F19 /deploy | Medium | not started | ❌ |
| F20 Prompt-with-Default | High | not started | ❌ |
| F21 /next | High | done | ✅ |
| F22 Colored Footer | High | done | ✅ |
