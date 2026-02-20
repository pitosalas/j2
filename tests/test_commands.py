"""Tests for scaffold/.claude/commands/ — verifies all command files exist and call runner correctly."""

from pathlib import Path

COMMANDS_DIR = Path(__file__).parent.parent / "scaffold" / ".claude" / "commands"

EXPECTED_COMMANDS = [
    "refresh",
    "features-gen",
    "features-refine",
    "tasks-gen",
    "tasks-refine",
    "task-start",
    "task-next",
    "try",
    "checkpoint",
    "milestone",
    "deploy",
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

def test_features_refine_passes_arguments_as_request():
    content = command_content("features-refine")
    assert "--request" in content
    assert "$ARGUMENTS" in content

def test_tasks_gen_passes_arguments_as_feature():
    content = command_content("tasks-gen")
    assert "--feature" in content
    assert "$ARGUMENTS" in content

def test_tasks_refine_splits_feature_and_request():
    content = command_content("tasks-refine")
    assert "--feature" in content
    assert "--request" in content
    assert "$ARGUMENTS" in content

def test_task_start_passes_feature_argument():
    content = command_content("task-start")
    assert "--feature" in content
    assert "--task" not in content
    assert "$ARGUMENTS" in content

def test_no_arg_commands_have_no_arguments_placeholder():
    # Commands that take no arguments should not reference $ARGUMENTS.
    for name in ("refresh", "features-gen", "task-next", "try", "checkpoint", "milestone"):
        content = command_content(name)
        assert "$ARGUMENTS" not in content, \
            f"{name}.md unexpectedly references $ARGUMENTS"
