# j2

A structured development framework for building software projects with [Claude Code](https://claude.ai/claude-code). j2 breaks development into explicit, user-controlled steps — from writing your first spec to shipping a tested feature — one slash command at a time.

> j2 was built using j2 itself.

## How It Works

You write a spec. j2 turns it into a feature list, breaks each feature into tasks, implements them one at a time, and enforces a quality gate before declaring anything done.

Each slash command calls Claude exactly once. You review the output, then decide what to run next — or just type `/continue` and j2 figures it out.

```
/refresh → /features-gen → /tasks-gen F01 → /task-next → /milestone F01 → /tasks-gen F02 → …
```

The inner loop is: **generate tasks for a feature → implement them one by one → milestone when done → repeat for the next feature.**

## Requirements

- Python 3.10+
- [Claude Code](https://claude.ai/claude-code)
- PyYAML (installed automatically by the install script)
- A git remote (optional, needed for `/checkpoint` push)

## Installation

**First time — setting up j2 itself:**

```bash
git clone https://github.com/pitosalas/j2.git
cd j2
```

**Starting a new project with j2:**

From inside the j2 directory in Claude Code:

```
/deploy ../my-new-project
```

Or from the shell:

```bash
bash scaffold/install.sh ../my-new-project
```

Both do the same thing: create the target directory and install the j2 scaffold into it.

## Getting Started

After installing into a new project directory:

1. **Open Claude Code** in the new project directory
2. **Edit `.j2/config/settings.yaml`** — set your project name, language, and platform
3. **Edit `.j2/rules.md`** — define your coding standards (see example below)
4. **Write your spec** — add one or more `.md` files to `.j2/specs/`
5. **Run `/refresh`** — Claude reads your spec, surfaces gaps, and rewrites it with suggested answers

### What goes in `rules.md`?

`rules.md` is injected into every command, so Claude always codes to your standards. Example:

```markdown
## Python
- Version 3.11
- Use pytest for all tests
- No bare `except` — always catch specific exception types
- f-strings only, no .format()

## Structure
- Files: no more than 300 lines
- Functions: no more than 30 lines

## Testing
- Every feature must have at least one test
- Run tests before declaring any task done
```

## Slash Commands

| Command | Argument | Purpose |
|---|---|---|
| `/refresh` | — | Summarize spec, surface gaps, rewrite with suggested answers |
| `/features-gen` | — | Generate prioritized feature list from spec |
| `/features-update` | — | Add, remove, or reprioritize features |
| `/tasks-gen` | `<feature-id>` | Generate task breakdown for a feature |
| `/tasks-update` | `<feature-id>` | Refine the task list for a feature |
| `/task-next` | — | Find and implement the next pending task automatically |
| `/task-start` | `<feature-id>` | Implement the next task in a specific feature |
| `/milestone` | `<feature-id>` | Quality gate: confirm tests pass, archive tasks, update README |
| `/checkpoint` | — | Save context to `.j2/current.md`, commit, and push to git |
| `/code-review` | — | Check all source files against `rules.md`; list violations as tasks |
| `/continue` | — | Run whatever the last command recommended as the next step |
| `/deploy` | `<target-dir>` | Bootstrap a new project from this repo |

**Feature IDs** (e.g. `F01`) default to the current in-progress feature if omitted.
**Open-ended inputs** (like a refinement request) are prompted interactively after invocation.

## The `/continue` Command

Every command ends by writing a `next:` recommendation to `.j2/state.md`. Running `/continue` reads that recommendation and executes it — so you can drive the entire workflow by just repeatedly typing `/continue`.

```
/continue   →  runs /refresh
/continue   →  runs /tasks-gen F01
/continue   →  runs /task-next
/continue   →  runs /task-next
/continue   →  runs /milestone F01
…
```

## Directory Structure

After installation, your project will contain:

```
.j2/
  rules.md          # Your coding principles — injected into every command
  specs/            # Your project spec (one or more .md files)
  features/         # Feature list with status tracking (auto-generated)
  tasks/            # Task breakdowns per feature (auto-generated)
  tasks/done/       # Archived task files after milestone
  config/
    settings.yaml   # Project name, language, platform
    workflow.yaml   # Maps commands to templates
  templates/        # Prompt templates (one per slash command)
  runner.py         # Template renderer — the engine behind every command
  current.md        # Working context saved by /checkpoint
  state.md          # Last completed/next recommendation (used by /continue)

.claude/
  commands/         # Slash command definitions
```

## Under the Hood

Each slash command is a tiny Markdown file that calls:

```bash
python3 .j2/runner.py <command> --root .
```

`runner.py` reads the matching template from `.j2/templates/`, injects context (your spec, feature list, task list, rules) via `{{placeholder}}` substitution, and prints the filled prompt for Claude to act on.

All state is plain Markdown and YAML — no database, no server, no lock-in. Every file is readable and editable by hand.

## Principles

- **One Claude call per command** — no automated loops; you review output at each step
- **All state in files** — inspect, edit, or roll back anything by hand
- **Idempotent** — re-running any command is always safe
- **No magic** — the rendered prompt is visible; you can read exactly what Claude was asked

## FAQ

**Do I have to follow the commands in order?**
No. The order is a sensible default, but you can re-run any command at any time. `/refresh` is safe to run again after you've already generated features. `/tasks-gen` can be re-run to regenerate a task list. All commands are idempotent.

**Can I edit the generated files by hand?**
Yes — that's the point. `features.md`, task files, `rules.md`, and spec files are all plain Markdown. Edit them freely. The next command will pick up whatever is on disk.

**How do I resume work after a break?**
Run `/continue`. It reads `.j2/state.md` (written by the last command) and picks up exactly where you left off. If you want more context, read `.j2/current.md` — that's what `/checkpoint` saves.

**What if I want to add a feature mid-project?**
Run `/features-update` and describe what you want to add. It will insert the new feature at the right priority level. Then run `/tasks-gen <new-feature-id>` and continue with `/task-next`.

**What if a task is too big or too vague?**
Run `/tasks-update <feature-id>` and ask Claude to split it or clarify it. The task file is also plain Markdown — you can edit it directly.

**What if Claude implements something wrong?**
Edit the code by hand or ask Claude to fix it in a follow-up message. Then mark the task done in the task file and run `/task-next` to continue. The task file is just Markdown — change any status field directly.

**Can I use j2 without git?**
Yes, except `/checkpoint` will fail at the commit/push step. Everything else works fine without git.

**What is `rules.md` actually for?**
It's injected into every prompt so Claude always codes to your standards — language version, test requirements, style rules, file size limits, etc. Update it any time; the next command will use the new version automatically.

**Does j2 work for non-Python projects?**
The framework itself is Python, but the projects it guides can be in any language. Set `language` in `settings.yaml` and write your `rules.md` for your target language. The prompt templates are language-agnostic.

**What's the difference between `/task-start` and `/task-next`?**
`/task-next` finds the next task automatically across all features. `/task-start <feature-id>` lets you pick a specific feature to work on. Use `/task-next` for normal flow; use `/task-start` when you want to jump to a particular feature.

## License

This project is licensed under the [MIT License](LICENSE).

Copyright (c) 2025 Pito Salas
