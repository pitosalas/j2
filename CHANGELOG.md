# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2025-01-01

### Added
- `/refresh` — read spec, surface gaps, rewrite with suggested answers
- `/features-gen` — generate prioritized feature list from spec
- `/features-update` — add, remove, or reprioritize features interactively
- `/tasks-gen` — generate task breakdown for a feature
- `/tasks-update` — refine the task list for a feature
- `/task-start` — implement the next task in a specific feature
- `/task-next` — automatically find and implement the next pending task
- `/milestone` — quality gate: confirm tests pass, archive tasks, update README
- `/checkpoint` — save context to `.j2/current.md`, commit, and push to git
- `/code-review` — check all source files against `rules.md`; list violations as tasks
- `/continue` — execute whatever the last command recommended as next step
- `/deploy` — bootstrap a new project from this repo into a target directory
- Colored structured footer written to terminal and `.j2/state.md` after every command
- Workflow-ordered next-step logic (spec gaps → tasks-gen → task-next)
- Task archiving to `.j2/tasks/done/` on milestone
- Completed features archive in `features.md`
- ROS2 configuration profile
- File-based state management — all state in plain Markdown and YAML
- `install.sh` scaffold deployment script
- GitHub Actions CI across Python 3.10, 3.11, 3.12
