# j2 Feature List

Status values:
- **Status**: `not started` / `in progress` / `done`
- **Tests written**: `no` / `yes`
- **Tests passing**: `n/a` / `no` / `yes`

---

<!-- ===== INCOMPLETE FEATURES (High → Medium → Low) ===== -->

<!-- ===== COMPLETED FEATURES (High → Medium → Low) ===== -->

## F40 — `/status` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: A new `/status` command that displays the current project health at a glance. Shows: spec file count, total features broken down by status (done / in progress / not started), features missing task files, count of pending tasks across all active task files, and last completed/next recommendation from `state.md`. Output is concise and human-readable — no raw file dumps.

---

## F39 — `/milestone` Project-Complete Gate
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: When `/milestone` is invoked without a feature ID, act as a project-wide completion gate. Scan `features.md` for any features that are not `done` — if any exist, list them and exit without making changes. Only if all features are `done`: run `pytest`, and if all tests pass, perform the equivalent of `/checkpoint` (write `current.md`, commit, and push). The existing single-feature milestone behavior (when a feature ID is provided) is unchanged.

---

## F38 — /adopt Re-run Mode: Surgical Update
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: When `/adopt` is run on a project that already has j2 installed (`.j2/` exists with `runner.py`, `config/`, and `templates/`), detect the re-run and switch to surgical update mode: refresh `runner.py`, `templates/`, and `config/` from the j2 dev repo master copies (same as install.sh rsync logic), merge any new slash commands into `.claude/commands/` without touching existing ones, and leave all user files (`specs/`, `features/`, `tasks/`, `rules.md`, `README.md`) completely untouched. Do not re-run the spec/feature generation steps. Exit with a summary of what was updated.

---

## F37 — Enforce Workflow Principles in Templates
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Enforce the three workflow principles added to the spec. Principle 3 (no programming without a task; no task without a feature) is entirely missing: add guards to `start_task.md`, `next_task.md`, and `run_all_tasks.md` to exit with a clear error if no task file exists, and to `gen_tasks.md` to exit if the feature ID is not in `features.md`. Fix two idempotency gaps: `milestone.md` should skip archiving if the task file is already in `done/`; `checkpoint.md` should skip the git commit if nothing has changed.

---

## F36 — Auto-Generate Tasks After /features-update Adds a Feature
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: When `/features-update` adds one or more new features to the feature list, it automatically generates a task file for each new feature (equivalent to running `/tasks-gen <feature-id>` for each). This eliminates the manual follow-up step. If `/features-update` only modifies or removes existing features (no new features added), no task generation occurs.

---

## F34 — `/adopt` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: One-time command for adding j2 to an existing project. Auto-detects project settings from marker files, generates a draft spec from the codebase, produces a feature list with existing work marked `done` (running tests to set test status), merges `.gitignore` and `.claude/` config without overwriting, and leaves the existing README untouched. After completion the project is fully j2-managed.

---

## F33 — `/features-parallel` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Scans the feature list for all not-done features that have task files. For each, launches a background Task agent to implement all not-started tasks sequentially (same behavior as `/task-run-all`). Agents work independently on separate features and do not modify shared files (`features.md`, `state.md`, `README.md`). After all agents complete, the user runs `/milestone` for each feature.

---

## F32 — `/task-run-all` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Implements every not-started task in a feature sequentially without pausing. Takes a feature ID as an inline argument (defaults to first in-progress or not-started feature). Reads the task file, implements each task in order, updates its status to `done`, then moves to the next. Runs the test suite after all tasks are done. Does not touch `features.md` or archive the task file — that is left to `/milestone`.

---

## F30 — Token Minimization in Templates
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Reduce token waste in slash command templates. Remove `{{spec}}` and `{{features}}` from task-execution templates (`start_task.md`, `next_task.md`) since the task file provides sufficient context. Add a runner function that filters `{{features}}` to strip done entries and replace them with a summary count. Trim verbose template prose. Runner output remains silent on success (errors to stderr only).

---

## F29 — `/deploy` Clean Export Mode
**Priority**: Medium
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: When `/deploy` is invoked from a deployed project (not the j2 dev repo), it creates a new directory containing the project in fully working form with all j2 infrastructure removed — no `.j2/`, no `scaffold/`, no `.claude/commands/`, no `runner.py`, and no other evidence that j2 was used. The result is a clean, standalone copy of the project that can be shipped or handed off independently. The two modes are distinguished by detecting whether a `scaffold/` directory exists (dev repo) or not (deployed project).

---

## F28 — Open Source Readiness
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Add the standard files and configuration expected by open source contributors: GitHub Actions CI, issue templates, CONTRIBUTING.md, README badges, a complete .gitignore, CHANGELOG.md, SECURITY.md, CODE_OF_CONDUCT.md, and linting/coverage config in pyproject.toml.

---

## F27 — Fix Code Review Violations
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Fixes all violations identified by `/code-review` against `rules.md`. Violations span three files: `runner.py` (missing file header comments, several 1-2 line wrapper functions that can be inlined), `test_runner.py` (missing file header, file exceeds 500-line limit), and `test_commands.py` (missing file header, 1-line wrapper functions). Each task addresses one violation with a concrete code change.

---

## F26 — `/code-review` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Reads `rules.md` and all source files in the project, performs a complete code review checking each file against every rule, and generates a task file listing concrete changes needed to bring the code into compliance. Each task describes a specific violation and the fix required. Output is written to `.j2/tasks/F26.md` in the standard task format so `/task-next` can drive remediation.

---

## F12 — Slash Command Registration
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Each slash command is a markdown file under `.claude/commands/` that invokes `runner.py` to render the appropriate template with injected context. Commands that require a feature ID or target path take it as an inline argument via `$ARGUMENTS` (e.g. `/tasks-gen F01`); if omitted, the runner falls back to a context-aware default. Commands that need open-ended input (e.g. a refinement request) still prompt interactively.

---

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

## F06 — `/features-update` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Prompts the user for a refinement request (e.g. "Add a caching feature"), offering a context-aware suggested default based on the current feature list. Applies the change and outputs the complete updated feature list. If the change implies a spec gap, also outputs an updated spec.

---

## F07 — `/tasks-gen` Command
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Prompts the user for a feature ID, suggesting the first not-started feature as the default. Generates a task breakdown for that feature and stores it at `.j2/tasks/<feature-id>.md`.

---

## F08 — `/tasks-update` Command
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

## F35 — Install Script Adopt Message
**Priority**: Medium
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Update `install.sh` to detect when the target directory already contains source files and print a message at the end: "Run /adopt to scan your existing codebase and generate a spec and feature list."

---

## F31 — Parallel-Safe Command Documentation
**Priority**: Medium
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Document which commands are parallel-safe (per-feature commands like `/task-start <FID>`, `/tasks-gen <FID>`, `/tasks-update <FID>`) and which require exclusive access (commands that modify shared files: `/features-update`, `/milestone`, `/checkpoint`). Added a Parallel Usage section to the README with a safe/exclusive command table.

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
**Description**: Saves current working context to `.j2/current.md` so the developer can resume later. Captures what is in progress, what was just completed, what is next, and any open questions. Before committing, scans all non-done features and marks any fully-completed feature (all tasks `done`) as `done` in `features.md`, running `pytest` to set test status. Unlike `/milestone`, this is not a quality gate — it can be run at any point during work.

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
