# Jacques2 Framework Specification

## Overview

Jacques2 is a structured software development framework that guides users through building software projects with Claude Code. It provides a step-by-step workflow driven by slash commands, where each command performs one discrete planning or development action. The framework is written in Python and designed to be used as a project starter template.

## Goals

- Provide a repeatable, guided workflow for developing software with Claude
- Make each planning step explicit and user-controlled (no automated loops)
- Support iterative refinement at each step before moving forward
- Be general-purpose initially, with tuning for ROS2 projects over time
- Be easy to install and use as a starting point for new projects

## Directory Structure

The framework is delivered as a directory tree that users copy or clone into a new project. It includes:

```
.planner/
  prompt.md           # Meta-instructions for Claude about the framework
  principles.md       # User-defined coding principles injected into all commands
  specs/              # User-provided or generated project specifications
  features/           # Generated feature lists (includes per-feature status tracking)
  tasks/              # Generated task breakdowns per feature
  config/             # YAML configuration files
  templates/          # Prompt templates used by each slash command
  hooks/              # Claude Code hooks that implement slash commands
```

## Configuration

All settings are stored in YAML files under `.planner/config/`. Key configuration files:

- `settings.yaml` — global framework settings (project name, language, target platform, principles file path)
- `workflow.yaml` — defines the ordered steps and which template each step uses

## Workflow Steps

The framework guides the user through a sequence of steps. Each step is triggered by a slash command and calls Claude once. The user may re-run any step or edit outputs before proceeding.

### Step 1: `/spec-review`
Reads the spec files from `.planner/specs/` and produces a summary and clarifying questions for the user.

### Step 2: `/gen-features`
Reads the spec and generates a numbered feature list in `.planner/features/`. Each feature has a name, brief description, priority (high/medium/low), and status fields (implementation status, tests written, tests passing).

### Step 3: `/refine-features`
Allows the user to interactively refine the feature list with Claude's help — adding, removing, or reprioritizing features.

### Step 4: `/gen-tasks`
For each feature, generates a task breakdown stored in `.planner/tasks/<feature-name>.md`. Tasks are concrete, actionable development steps.

### Step 5: `/refine-tasks`
Interactive refinement of task lists for a given feature.

### Step 6: `/start-task`
Begins implementation of a specified task. Claude reads the task description and writes code.

### Step 7: `/milestone`
Copies all project files into a timestamped snapshot directory for safe testing.

## Slash Command Implementation

Each slash command is implemented as a Claude Code hook. Hooks read prompt templates from `.planner/templates/`, inject relevant context (spec files, feature lists, etc.), and call Claude once to produce output.

## Install Script

An `install.sh` shell script is provided to:
- Verify Python version (3.10+)
- Create the required directory structure if missing
- Copy template files into place
- Register Claude Code hooks
- Validate YAML configuration

## Target Platform

- **Language**: Python 3.10+
- **Initial target**: General-purpose software projects
- **Future target**: ROS2 packages and workspaces

## Constraints and Principles

- Each slash command invokes Claude exactly once — no automated multi-step loops
- The user reviews and approves output at each step before proceeding
- All state is stored in files (YAML and Markdown), not in memory
- No external dependencies beyond Python standard library and PyYAML
- Framework directories are prefixed with `.planner/` to stay out of the way of project code
