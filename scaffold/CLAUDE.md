# Project Instructions

This project uses the j2 framework for structured development with Claude Code.

## Coding Rules

Read and follow `.j2/rules.md` for all code you write in this project. These rules cover language version, testing, style, and packaging requirements.

## Project Context

- Spec: `.j2/specs/` — the project specification
- Features: `.j2/features/features.md` — the feature list with status tracking
- Tasks: `.j2/tasks/<feature-id>.md` — task breakdowns per feature
- Config: `.j2/config/settings.yaml` and `workflow.yaml`

## Workflow

Use slash commands to move through the development workflow one step at a time:

| Command | Purpose |
|---|---|
| `/spec-review` | Summarize spec and surface clarifying questions |
| `/gen-features` | Generate feature list from spec |
| `/refine-features <request>` | Add, remove, or reprioritize features |
| `/gen-tasks <feature-id>` | Generate task breakdown for a feature |
| `/refine-tasks <feature-id> <request>` | Refine tasks for a feature |
| `/start-task <feature-id> <task-id>` | Implement a specific task |
| `/next-task` | Implement the next pending task automatically |
| `/checkpoint` | Save current working context |
| `/try` | Snapshot project for experimentation |
| `/milestone` | Declare a feature complete (quality gate) |
