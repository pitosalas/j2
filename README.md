# j2

A structured software development framework for building projects with [Claude Code](https://claude.ai/claude-code). j2 guides you through each phase of development — from spec to shipping — one slash command at a time.

## What It Does

j2 breaks development into explicit, user-controlled steps:

1. **Refine your spec** — Claude surfaces gaps and rewrites the spec with suggested answers
2. **Generate features** — A prioritized, trackable feature list from the spec
3. **Break down tasks** — Concrete, actionable tasks per feature
4. **Implement** — Claude writes code one task at a time, marking tasks done as it goes
5. **Milestone** — A quality gate: tests must be written and passing before a feature is declared done

Every command writes a `next:` recommendation to `.j2/state.md`, so `/continue` always knows what to do next.

> j2 was built using j2 itself.

## Requirements

- Python 3.10+
- [Claude Code](https://claude.ai/claude-code)
- PyYAML (installed automatically)

## Installation

Clone the j2 repo, then deploy a new project from within Claude Code:

```
/deploy ../my-new-project
```

Or run the installer directly from the shell:

```bash
git clone https://github.com/yourname/j2.git
cd j2
bash scaffold/install.sh ../my-new-project
```

Then open Claude Code in the new project directory and run `/refresh` to begin.

## Getting Started

After installation, four things to do before your first command:

1. **Edit settings** — `.j2/config/settings.yaml` (project name, language, platform)
2. **Write your rules** — `.j2/rules.md` (language version, testing requirements, style conventions)
3. **Add your spec** — one or more `.md` files in `.j2/specs/`
4. **Run `/refresh`** in Claude Code

## Slash Commands

| Command | Argument | Purpose |
|---|---|---|
| `/refresh` | — | Summarize spec, surface gaps, rewrite with suggested answers |
| `/features-gen` | — | Generate prioritized feature list from spec |
| `/features-update` | — | Add, remove, or reprioritize features (prompts for request) |
| `/tasks-gen` | `<feature-id>` | Generate task breakdown for a feature |
| `/tasks-update` | `<feature-id>` | Update tasks for a feature (prompts for request) |
| `/task-start` | `<feature-id>` | Implement the next not-started task in a feature |
| `/task-next` | — | Automatically find and implement the next pending task |
| `/checkpoint` | — | Save working context to `.j2/current.md` |
| `/milestone` | `<feature-id>` | Quality gate: declare a feature done, archive task file, update README |
| `/code-review` | — | Review all source files against `rules.md`; output violations as a task list |
| `/continue` | — | Run whatever command `state.md` recommends next |
| `/deploy` | `<target-dir>` | Bootstrap a new project from this repo |

Feature IDs (e.g. `F01`) default to the current in-progress feature if omitted. Commands that need open-ended text input (like a refinement request) prompt interactively after invocation.

## Workflow

```
/refresh → /features-gen → /features-update → /tasks-gen F01 → /task-next → /milestone F01 → …
```

Or just keep running `/continue` — it reads `state.md` and always knows the right next step.

## Directory Structure

```
.j2/
  rules.md          # Your coding principles (injected into every command)
  specs/            # Your project spec (one or more .md files)
  features/         # Generated feature list with status tracking
  tasks/            # Task breakdowns per feature
  tasks/done/       # Archived task files after milestone
  config/           # Framework configuration (settings.yaml, workflow.yaml)
  templates/        # Prompt templates (one per slash command)
  runner.py         # Template renderer

.claude/
  commands/         # Slash command definitions

scaffold/           # Source files deployed to new projects via /deploy
```

## How It Works

Each slash command calls `python3 .j2/runner.py <command>`, which:

1. Reads the appropriate template from `.j2/templates/`
2. Injects context (spec, features, tasks, rules) via `{{placeholder}}` substitution
3. Prints the filled prompt for Claude to act on

All state lives in plain Markdown and YAML files — no database, no server, nothing to install beyond Python and PyYAML.

## Principles

- **One Claude call per command** — no automated loops; you review output at each step
- **All state in files** — everything is readable and editable by hand
- **Idempotent commands** — re-running any command is always safe
- **Inline arguments** — commands that need a feature ID or path take it on the same line (e.g. `/tasks-gen F01`); open-ended inputs are prompted interactively
- **No magic** — the rendered prompt is visible; you can read exactly what Claude was asked

## License

MIT
