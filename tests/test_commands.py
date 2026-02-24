#!/usr/bin/env python3
"""Tests for scaffold/.claude/commands/ — verifies all command files exist and call runner correctly."""
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

from pathlib import Path

COMMANDS_DIR = Path(__file__).parent.parent / ".claude" / "commands"

EXPECTED_COMMANDS = [
    "refresh",
    "features-gen",
    "features-update",
    "features-parallel",
    "tasks-gen",
    "tasks-update",
    "task-start",
    "task-next",
    "task-run-all",
    "checkpoint",
    "milestone",
    "code-review",
    "deploy",
    "adopt",
    "continue",
]


# --- existence ---

def test_all_command_files_exist():
    for name in EXPECTED_COMMANDS:
        assert (COMMANDS_DIR / f"{name}.md").exists(), f"Missing command file: {name}.md"


# --- runner invocation ---

def test_each_command_calls_runner():
    for name in EXPECTED_COMMANDS:
        content = (COMMANDS_DIR / f"{name}.md").read_text()
        assert "runner.py" in content, f"{name}.md does not call runner.py"

def test_each_command_passes_correct_id():
    for name in EXPECTED_COMMANDS:
        content = (COMMANDS_DIR / f"{name}.md").read_text()
        assert f"runner.py {name}" in content, \
            f"{name}.md does not pass '{name}' as command ID to runner"


# --- argument wiring ---

def test_features_refine_is_interactive_no_inline_args():
    # features-update prompts interactively; it must NOT pass $ARGUMENTS inline.
    content = (COMMANDS_DIR / "features-update.md").read_text()
    assert "$ARGUMENTS" not in content

def test_tasks_gen_passes_feature_argument():
    content = (COMMANDS_DIR / "tasks-gen.md").read_text()
    assert "--feature" in content
    assert "$ARGUMENTS" in content

def test_tasks_refine_passes_feature_argument():
    # tasks-update takes feature ID inline; refinement request is prompted interactively.
    content = (COMMANDS_DIR / "tasks-update.md").read_text()
    assert "--feature" in content
    assert "$ARGUMENTS" in content

def test_task_start_passes_feature_argument():
    content = (COMMANDS_DIR / "task-start.md").read_text()
    assert "--feature" in content
    assert "--task" not in content
    assert "$ARGUMENTS" in content

def test_milestone_passes_feature_argument():
    content = (COMMANDS_DIR / "milestone.md").read_text()
    assert "--feature" in content
    assert "$ARGUMENTS" in content

def test_deploy_passes_target_argument():
    content = (COMMANDS_DIR / "deploy.md").read_text()
    assert "--target" in content
    assert "$ARGUMENTS" in content

def test_no_arg_commands_have_no_arguments_placeholder():
    # Commands that take no arguments should not reference $ARGUMENTS.
    for name in ("refresh", "features-gen", "features-update", "features-parallel", "task-next", "checkpoint", "continue", "code-review", "adopt"):
        content = (COMMANDS_DIR / f"{name}.md").read_text()
        assert "$ARGUMENTS" not in content, \
            f"{name}.md unexpectedly references $ARGUMENTS"
