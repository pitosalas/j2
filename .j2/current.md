# j2 Current Checkpoint
Date: 2026-02-20

## What was just completed

- `/refresh` run: spec reviewed, 4 clarifying questions surfaced with suggested answers, updated spec produced in fenced code block.
- Bug fix: `next_task.md` and `start_task.md` templates updated so that when the last task in a feature's task file is marked done, Claude automatically runs `mv .j2/tasks/<feature-id>.md .j2/tasks/done/<feature-id>.md`.
- `runner.py` `load_tasks()` updated to fall back to `tasks/done/` if active task file not found (so `/milestone` still works on already-archived files).
- `milestone.md` updated to skip the `mv` step if the task file is already in `done/`.

## What is currently in progress

Nothing — all features are `done`. The project is in a clean, complete state.

## What is next

- If new features are desired, run `/features-refine` to add them, then `/tasks-gen` and `/task-next`.
- Otherwise, the framework is ready for `/deploy` to a real project.

## Open questions

- Should `rsync --ignore-existing` be changed to force-copy for master files (runner.py, templates/, config/) so framework updates propagate on reinstall? (Suggested: yes — spec updated to reflect this, but install.sh not yet changed.)
- Should `snapshots/` be added to `.gitignore` by install.sh? (Suggested: yes — spec updated, install.sh not yet changed.)

## Feature Status Summary

| Feature | Name | Priority | Status |
|---------|------|----------|--------|
| F01 | Directory Structure Scaffold | High | done |
| F02 | YAML Configuration System | High | done |
| F03 | Prompt Template System | High | done |
| F04 | /refresh Command | High | done |
| F05 | /features-gen Command | High | done |
| F06 | /features-refine Command | High | done |
| F07 | /tasks-gen Command | High | done |
| F08 | /tasks-refine Command | High | done |
| F09 | /task-start Command | High | done |
| F10 | /milestone Command | High | done |
| F12 | Slash Command Registration | High | done |
| F13 | File-Based State Management | High | done |
| F15 | Principles File | High | done |
| F18 | /task-next Command | High | done |
| F21 | /continue Command | High | done |
| F22 | Colored Structured Footer | High | done |
| F23 | Workflow-Ordered Next Step Logic | High | done |
| F11 | Install Script | Medium | done |
| F16 | /checkpoint Command | Medium | done |
| F17 | /try Command | Medium | done |
| F19 | /deploy Command | Medium | done |
| F20 | Prompt-with-Default Input Pattern | Medium | done |
| F24 | Completed Tasks Archive | Medium | done |
| F25 | Completed Features Archive | Medium | done |
| F14 | ROS2 Configuration Profile | Low | done |
