# j2 Feature List

Status values:
- **Status**: `not started` / `in progress` / `done`
- **Tests written**: `no` / `yes`
- **Tests passing**: `n/a` / `no` / `yes`

---

<!-- ===== INCOMPLETE FEATURES (High → Medium → Low) ===== -->

## F12 — Slash Command Registration
**Priority**: High
**Status**: in progress | Tests written: no | Tests passing: n/a
**Description**: Each slash command is a markdown file under `.claude/commands/` that invokes `runner.py` to render the appropriate template with injected context. Commands that require a feature ID or target path take it as an inline argument via `$ARGUMENTS` (e.g. `/tasks-gen F01`); if omitted, the runner falls back to a context-aware default. Commands that need open-ended input (e.g. a refinement request) still prompt interactively.

---

<!-- ===== COMPLETED FEATURES (High → Medium → Low) ===== -->

## F10 — `/milestone` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Marks a feature as complete. Confirms implementation is done, tests are written and passing, and code is cleaned up. Acts as a quality gate: if tests are missing or failing, the milestone is not granted. On success: moves the task file to `tasks/done/`, moves the feature entry in `features.md` from the incomplete section to the completed section in priority order, and reviews the spec and codebase to update `README.md` to reflect the current state of the project.

---

## F01 — Directory Structure Scaffold
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: The framework ships with a predefined `.j2/` directory tree (specs, features, tasks, config, templates). An install script creates any missing directories and puts template files in place.

---

## F02 — YAML Configuration System
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: All settings are stored in YAML files under `.j2/config/`. Includes `settings.yaml` (project name, language, platform) and `workflow.yaml` (ordered steps and template mappings). The framework reads these at runtime to configure behavior.

---

## F03 — Prompt Template System
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Each workflow step has a Markdown prompt template stored in `.j2/templates/`. Templates use `{{placeholder}}` tokens (e.g. `{{spec}}`, `{{features}}`, `{{rules}}`) that are filled in at runtime before being sent to Claude.

---

## F04 — `/refresh` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Reads all files in `.j2/specs/`, summarizes the project, surfaces clarifying questions each paired with a suggested answer, then rewrites the spec incorporating those answers and presents it in a fenced code block.

---

## F05 — `/features-gen` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Reads the spec and creates or updates the numbered feature list in `.j2/features/features.md`. If a feature list already exists, updates it rather than replacing it wholesale — preserving existing status values and adding or revising entries as needed.

---

## F06 — `/features-refine` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Prompts the user for a refinement request (e.g. "Add a caching feature"), offering a context-aware suggested default based on the current feature list. Applies the change and outputs the complete updated feature list. If the change implies a spec gap, also outputs an updated spec.

---

## F07 — `/tasks-gen` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Prompts the user for a feature ID, suggesting the first not-started feature as the default. Generates a task breakdown for that feature and stores it at `.j2/tasks/<feature-id>.md`.

---

## F08 — `/tasks-refine` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Prompts the user for a feature ID and a refinement request, offering sensible defaults. Applies the changes to that feature's task list.

---

## F09 — `/task-start` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Prompts the user for a feature ID, suggesting the first in-progress or not-started feature as the default. Finds the first not-started task in that feature and implements it.

---

## F13 — File-Based State Management
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: All workflow state (spec, feature list, task lists) is stored as files on disk. No in-memory state is required between steps. This makes the workflow inspectable, editable, and resumable at any point. Satisfied by the runner's design.

---

## F15 — Principles File
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: A `.j2/rules.md` file holds user-defined coding principles (e.g. testing requirements, language version, style rules). The runner injects its contents into every template via `{{rules}}` at command time, so updating the file automatically propagates to all workflow steps. The scaffold ships a default `rules.md` that users customize for their project.

---

## F18 — `/task-next` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Takes no arguments and prompts for none. Automatically determines the logical next task by scanning the feature list for the first in-progress or not-started feature, then finding the first not-started task within it, and begins implementation. Exits with a clear error if no logical next task can be determined.

---

## F21 — `/continue` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Every command footer writes a structured state block to `.j2/state.md` containing: `completed:` (what was just done), `state:` (project health counts), and `next:` (recommended slash command). The `/continue` command reads `next:` from `.j2/state.md` and executes it as if the user typed it, advancing the workflow with a single keystroke.

---

## F22 — Colored Structured Footer
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Every command ends with a color-highlighted footer using ANSI codes (or Claude Code markdown) containing three lines: `completed:` (one sentence — what was just done), `state:` (three counts: spec items without features / features without task files / tasks not yet run), and `next:` (the exact slash command to run next). The footer is visually distinct so it stands out from command output. These three values are also written to `.j2/state.md` for use by `/continue`.

---

## F23 — Workflow-Ordered Next Step Logic
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Every command's footer `next:` recommendation must follow a strict priority order: (1) if spec gaps exist, recommend `/refresh`; (2) else if any not-done feature (highest priority first) lacks a task file, recommend `/tasks-gen <feature-id>`; (3) else recommend `/task-next` to execute the first pending task in the highest-priority not-done feature. This ordering is enforced in the footer instructions appended by `runner.py` (the `FOOTER` constant) so every command automatically produces a correctly-ordered `next:` recommendation.

---

## F25 — Completed Features Archive
**Priority**: Medium
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: After `/milestone` grants a feature complete, the feature's entry is moved from the incomplete section to the completed section of `.j2/features/features.md`, maintaining priority order (High → Medium → Low) within each section. The `/milestone` template instructs Claude to perform this reorder as part of granting the milestone.

---

## F11 — Install Script
**Priority**: Medium
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: A `install.sh` shell script that verifies Python 3.10+, installs PyYAML if missing, creates the required `.j2/` directory structure, copies scaffold files using `rsync --ignore-existing` so existing user files are never overwritten, and validates YAML config files.

---

## F16 — `/checkpoint` Command
**Priority**: Medium
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Saves current working context to `.j2/current.md` so the developer can resume later. Captures what is in progress, what was just completed, what is next, and any open questions. Unlike `/milestone`, this is not a quality gate — it can be run at any point during work.

---

## F17 — `/try` Command
**Priority**: Medium
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Copies all project files into a timestamped snapshot directory (e.g., `snapshots/2026-02-20T0707/`) so the developer can play with and test the current state as if it were a standalone project, without affecting the working directory. No quality checks — just a raw snapshot for experimentation.

---

## F19 — `/deploy` Command
**Priority**: Medium
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Prompts the user for a target directory path (suggesting a sensible default). Creates that directory and runs `install.sh` on it to bootstrap a fresh j2 project. Used to deploy the scaffold from the dev repo to a new project.

---

## F24 — Completed Tasks Archive
**Priority**: Medium
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: After `/milestone` grants a feature complete, the feature's task file (`.j2/tasks/<feature-id>.md`) is moved to `.j2/tasks/done/<feature-id>.md`. This keeps the active tasks directory focused on pending work. The runner's `missing_tasks_summary` function checks both `.j2/tasks/` and `.j2/tasks/done/` so archived features are not re-flagged as missing task files. The scaffold ships with the `tasks/done/` directory pre-created.

---

## F14 — ROS2 Configuration Profile
**Priority**: Low
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: A ROS2-specific configuration profile (YAML) and prompt templates that tailor feature and task generation for ROS2 packages, nodes, topics, and launch files.
