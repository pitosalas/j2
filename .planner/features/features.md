# Jacques2 Feature List

Status values:
- **Status**: `not started` / `in progress` / `done`
- **Tests written**: `no` / `yes`
- **Tests passing**: `n/a` / `no` / `yes`

---

## F01 — Directory Structure Scaffold
**Priority**: High
**Status**: done | Tests written: no | Tests passing: n/a
**Description**: The framework ships with a predefined `.planner/` directory tree (specs, features, tasks, config, templates, hooks). An install script creates any missing directories and puts template files in place.

---

## F02 — YAML Configuration System
**Priority**: High
**Status**: done | Tests written: no | Tests passing: n/a
**Description**: All settings are stored in YAML files under `.planner/config/`. Includes `settings.yaml` (project name, language, platform) and `workflow.yaml` (ordered steps and template mappings). The framework reads these at runtime to configure behavior.

---

## F03 — Prompt Template System
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Each workflow step has a Markdown prompt template stored in `.planner/templates/`. Templates use placeholders (e.g., `{{spec}}`, `{{features}}`, `{{rules}}`) that are filled in at runtime before being sent to Claude.

---

## F04 — `/spec-review` Command
**Priority**: Medium
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Reads all files in `.planner/specs/`, summarizes the project, and produces clarifying questions for the user. Output is written to `.planner/features/spec-review.md`.

---

## F05 — `/gen-features` Command
**Priority**: High
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Reads the spec and generates a numbered feature list with name, description, and priority. Output is written to `.planner/features/features.md`.

---

## F06 — `/refine-features` Command
**Priority**: High
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Presents the current feature list and allows the user to iteratively add, remove, or reprioritize features with Claude's help. Updates `features.md` in place.

---

## F07 — `/gen-tasks` Command
**Priority**: High
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: For each feature in the feature list, generates a task breakdown with concrete, actionable development steps. Each feature gets its own file at `.planner/tasks/<feature-name>.md`.

---

## F08 — `/refine-tasks` Command
**Priority**: High
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Presents the task list for a specified feature and allows iterative refinement. Updates the relevant task file in place.

---

## F09 — `/start-task` Command
**Priority**: High
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Takes a feature name and task identifier, reads the task description, and begins implementation. Claude writes code for the specified task.

---

## F10 — `/milestone` Command
**Priority**: Medium
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Marks a feature as complete. Confirms implementation is done, tests are written and passing, and code is cleaned up. Summarizes what was completed and updates feature status. This is a quality gate, not just a snapshot.

---

## F11 — Install Script
**Priority**: Medium
**Status**: done | Tests written: no | Tests passing: n/a
**Description**: A `install.sh` shell script that verifies Python 3.10+, creates the directory structure, copies template files, registers Claude Code hooks, and validates YAML configuration.

---

## F12 — Hook Registration for Slash Commands
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Each slash command is registered as a Claude Code hook. Hooks read the appropriate template, inject context from files on disk, and invoke Claude exactly once per command invocation.

---

## F13 — File-Based State Management
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: All workflow state (spec, feature list, task lists) is stored as files on disk. No in-memory state is required between steps. This makes the workflow inspectable, editable, and resumable at any point. Satisfied by the runner's design.

---

## F14 — ROS2 Configuration Profile
**Priority**: Low
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: A ROS2-specific configuration profile (YAML) and prompt templates that tailor feature and task generation for ROS2 packages, nodes, topics, and launch files.

---

## F15 — Principles File
**Priority**: High
**Status**: done | Tests written: no | Tests passing: n/a
**Description**: A `.planner/rules.md` file holds user-defined coding principles (e.g. testing requirements, language version, style rules). The runner injects its contents into every template via `{{rules}}` at command time, so updating the file automatically propagates to all workflow steps. The scaffold ships a default `rules.md` that users customize for their project.

---

## F16 — `/checkpoint` Command
**Priority**: Medium
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Saves current working context to `.planner/current.md` so the developer can resume later. Captures what is in progress, what was just completed, what is next, and any open questions. Unlike `/milestone`, this is not a quality gate — it can be run at any point during work.

---

## F17 — `/try` Command
**Priority**: Medium
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Copies all project files into a timestamped snapshot directory (e.g., `snapshots/2026-02-18T1045/`) so the developer can play with and test the current state as if it were a standalone project, without affecting the working directory. No quality checks — just a raw snapshot for experimentation.

---

## F18 — `/next-task` Command
**Priority**: High
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Automatically determines and starts the next pending task. Reads the feature list to find the first in-progress or not-started feature, reads its task file to find the first not-started task, then implements it. Eliminates the need to manually track which feature and task to work on next.

---
