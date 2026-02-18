# Jacques2 — Current State

## What this project is
Jacques2 is a structured software development framework that guides users through building software with Claude Code. It uses slash commands, each invoking Claude exactly once, to move through planning steps: spec review → feature list → task breakdown → implementation. All state is file-based. The framework ships as a `scaffold/` directory that users copy into their projects via `install.sh`.

## Repository layout
```
jacques2/
  pyproject.toml               # uv project: pyyaml + pytest
  .venv/                       # uv virtual environment
  .planner/                    # planning files for developing jacques2 itself
    prompt.md                  # meta-instructions
    rules.md              # coding principles (apply to all code)
    specs/
      jacques2.md              # project spec
    features/
      features.md              # feature list with status tracking
    current.md                 # this file
  scaffold/                    # what ships to users
    install.sh                 # copies scaffold, checks Python 3.10+, validates YAML
    .planner/
      rules.md            # default principles (users customize)
      config/
        settings.yaml          # paths config + rules_file key
        workflow.yaml          # 7 workflow steps with command→template mapping
      specs/
        README.md              # tells user to put spec here
      features/.gitkeep
      tasks/.gitkeep
      hooks/.gitkeep
      templates/               # prompt templates for each command
        spec_review.md         # uses {{spec}}
        gen_features.md        # uses {{rules}}, {{spec}}
        refine_features.md     # uses {{features}}, {{request}}
        gen_tasks.md           # uses {{rules}}, {{spec}}, {{feature}}
        refine_tasks.md        # uses {{tasks}}, {{request}}
        start_task.md          # uses {{rules}}, {{spec}}, {{feature}}, {{task}}
        milestone.md           # uses {{features}}
      runner.py                # THE RUNNER (see below)
  tests/
    test_runner.py             # 17 tests, all passing
```

## Principles (from .planner/rules.md)
- Each feature must have at least one test
- Python 3.10+
- Type annotations sparingly
- No relative imports
- All imports at the top
- Intention-revealing names
- Functions: 1-2 line comment at top max
- Use uv for packaging/virtual environments

## The runner (scaffold/.planner/runner.py)
Core module — fills a template with context from disk and prints filled prompt to stdout.

**CLI:**
```
python .planner/runner.py <command-id> [--feature F01] [--task T01] [--request "text"] [--root PATH]
```

**Functions:**
- `load_config(root)` — reads settings.yaml
- `load_workflow(root)` — reads workflow.yaml steps list
- `find_step(workflow, command_id)` — finds step by id, raises ValueError if missing
- `load_template(root, settings, template_name)` — reads template file
- `find_placeholders(template)` — returns set of {{name}} tokens
- `load_spec(root, settings)` — concatenates all .md files in specs_dir
- `load_features(root, settings)` — reads features_file
- `load_rules(root, settings)` — reads rules_file
- `load_tasks(root, settings, feature_id)` — reads tasks_dir/<feature_id>.md
- `extract_feature(features_text, feature_id)` — extracts ## F01 section from markdown
- `extract_task(tasks_text, task_id)` — extracts ### T01 section from markdown
- `fill_template(template, context)` — replaces {{key}} tokens
- `build_context(root, settings, placeholders, args)` — dispatches loaders by placeholder
- `main()` — CLI entry point

**Placeholder → loader mapping:**
| Placeholder | Source |
|---|---|
| `{{spec}}` | all .md files in specs_dir concatenated |
| `{{rules}}` | rules_file |
| `{{features}}` | features_file |
| `{{feature}}` | extracted section from features_file by --feature ID |
| `{{tasks}}` | tasks_dir/<feature_id>.md |
| `{{task}}` | extracted section from tasks file by --task ID |
| `{{request}}` | --request CLI arg |

## Feature status
| ID | Feature | Status |
|----|---------|--------|
| F01 | Directory Structure Scaffold | done (scaffold/ exists) |
| F02 | YAML Configuration System | done (settings.yaml, workflow.yaml) |
| F03 | Prompt Template System | done (runner.py fills templates) |
| F04 | /spec-review command | not started |
| F05 | /gen-features command | not started |
| F06 | /refine-features command | not started |
| F07 | /gen-tasks command | not started |
| F08 | /refine-tasks command | not started |
| F09 | /start-task command | not started |
| F10 | /milestone command | not started |
| F11 | Install Script | done (install.sh) |
| F12 | Hook Registration for Slash Commands | not started — NEXT |
| F13 | File-Based State Management | done (all state in files, no memory) |
| F14 | ROS2 Configuration Profile | not started (low priority) |
| F15 | Principles File | done |

## What was next (interrupted)
**F12 — Hook Registration for Slash Commands**

Plan: create `scaffold/.claude/commands/` with one `.md` file per command. Each file uses shell substitution to call runner.py and inject its output as the Claude prompt.

Example for spec-review.md:
```
$(python3 .planner/runner.py spec-review)
```

Example for gen-tasks.md (needs feature ID from user):
```
$(python3 .planner/runner.py gen-tasks --feature $ARGUMENTS)
```

Example for start-task.md (needs feature + task ID):
```
$(python3 .planner/runner.py start-task \
  --feature $(echo "$ARGUMENTS" | awk '{print $1}') \
  --task $(echo "$ARGUMENTS" | awk '{print $2}'))
```

Commands and their argument needs:
- `spec-review` — no args
- `gen-features` — no args
- `refine-features` — `--request "$ARGUMENTS"`
- `gen-tasks` — `--feature $ARGUMENTS`
- `refine-tasks` — feature ID (first word) + request (rest): needs arg splitting
- `start-task` — feature ID (first word) + task ID (second word)
- `milestone` — no args

Also need to:
- Update install.sh to ensure `.claude/commands/` is created
- Write tests verifying command files exist and call runner correctly
- Update features.md status for completed features

## Test status
`uv run pytest` → 17 passed, 0 failed
