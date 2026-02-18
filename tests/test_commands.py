"""Tests for scaffold/.claude/commands/ — verifies all command files exist and call runner correctly."""

from pathlib import Path

COMMANDS_DIR = Path(__file__).parent.parent / "scaffold" / ".claude" / "commands"

EXPECTED_COMMANDS = [
    "spec-review",
    "gen-features",
    "refine-features",
    "gen-tasks",
    "refine-tasks",
    "start-task",
    "next-task",
    "try",
    "checkpoint",
    "milestone",
]


def command_file(name):
    # Return the Path for a given command file.
    return COMMANDS_DIR / f"{name}.md"


def command_content(name):
    # Return the text content of a command file.
    return command_file(name).read_text()


# --- existence ---

def test_all_command_files_exist():
    for name in EXPECTED_COMMANDS:
        assert command_file(name).exists(), f"Missing command file: {name}.md"


# --- runner invocation ---

def test_each_command_calls_runner():
    for name in EXPECTED_COMMANDS:
        content = command_content(name)
        assert "runner.py" in content, f"{name}.md does not call runner.py"

def test_each_command_passes_correct_id():
    for name in EXPECTED_COMMANDS:
        content = command_content(name)
        assert f"runner.py {name}" in content, \
            f"{name}.md does not pass '{name}' as command ID to runner"


# --- argument wiring ---

def test_refine_features_passes_arguments_as_request():
    content = command_content("refine-features")
    assert "--request" in content
    assert "$ARGUMENTS" in content

def test_gen_tasks_passes_arguments_as_feature():
    content = command_content("gen-tasks")
    assert "--feature" in content
    assert "$ARGUMENTS" in content

def test_refine_tasks_splits_feature_and_request():
    content = command_content("refine-tasks")
    assert "--feature" in content
    assert "--request" in content
    assert "$ARGUMENTS" in content

def test_start_task_splits_feature_and_task():
    content = command_content("start-task")
    assert "--feature" in content
    assert "--task" in content
    assert "$ARGUMENTS" in content

def test_no_arg_commands_have_no_arguments_placeholder():
    # Commands that take no arguments should not reference $ARGUMENTS.
    for name in ("spec-review", "gen-features", "next-task", "try", "checkpoint", "milestone"):
        content = command_content(name)
        assert "$ARGUMENTS" not in content, \
            f"{name}.md unexpectedly references $ARGUMENTS"
