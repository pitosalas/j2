# Checkpoint — 2026-02-18

## What was just completed

- F05–F09 done: `/gen-features`, `/refine-features`, `/gen-tasks`, `/refine-tasks`, `/start-task` — templates improved and end-to-end rendering tests written for each
- Template improvements: status header in gen_features, status preservation notes in refine_features/refine_tasks, post-implementation instructions in start_task, status field in gen_tasks task format
- Bug fix: `extract_feature` / `extract_task` now accept lowercase IDs (f01, t01)
- `scaffold/CLAUDE.md` added — tells Claude to read `.j2/rules.md` in new projects; copied by install.sh automatically
- `install.sh` next steps updated to mention `rules.md`
- 44 tests passing

## What is currently in progress

F11 (Install Script) — `install.sh` works but has no tests and no Jinja2 dependency check.

## What is next

1. Close out F11: add Jinja2 check to `install.sh`, write tests
2. F18 `/next-task` — High priority, needs task-scanning logic in runner.py
3. F10 `/milestone`, F16 `/checkpoint`, F17 `/try` — Medium priority command features needing tests
4. F04 `/spec-review` — Medium priority

## Open questions

- F18 `/next-task`: runner needs to parse `**Status**: not started` fields in task files — confirm this approach before implementing
- F14 ROS2 profile: still low priority, skip for now?

## Feature status

| ID | Feature | Status | Tests |
|----|---------|--------|-------|
| F01 | Directory Scaffold | done | ✓ |
| F02 | YAML Config | done | ✓ |
| F03 | Template System | done | ✓ |
| F04 | `/spec-review` | not started | — |
| F05 | `/gen-features` | done | ✓ |
| F06 | `/refine-features` | done | ✓ |
| F07 | `/gen-tasks` | done | ✓ |
| F08 | `/refine-tasks` | done | ✓ |
| F09 | `/start-task` | done | ✓ |
| F10 | `/milestone` | not started | — |
| F11 | Install Script | in progress | — |
| F12 | Slash Commands | done | ✓ |
| F13 | File-Based State | done | ✓ |
| F14 | ROS2 Profile | not started | — |
| F15 | Principles File | done | ✓ |
| F16 | `/checkpoint` | not started | — |
| F17 | `/try` | not started | — |
| F18 | `/next-task` | not started | — |
