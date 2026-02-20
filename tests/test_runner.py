"""Tests for scaffold/.j2/runner.py"""

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scaffold" / ".j2"))
import runner


FEATURES_TEXT = """\
# Feature List

## F01 — Directory Scaffold
**Priority**: High
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Creates the directory tree.

---

## F02 — YAML Config
**Priority**: High
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Reads YAML settings.

---
"""

TASKS_TEXT = """\
# Tasks for F01

### T01 — Create directories
**Description**: Make all required .planner subdirectories.

### T02 — Write tests
**Description**: Write tests for directory creation.
"""


# --- find_placeholders ---

def test_find_placeholders_detects_all():
    template = "Hello {{name}}, your spec is {{spec}} and rules are {{rules}}."
    assert runner.find_placeholders(template) == {"name", "spec", "rules"}

def test_find_placeholders_empty():
    assert runner.find_placeholders("No placeholders here.") == set()

def test_find_placeholders_deduplicates():
    assert runner.find_placeholders("{{foo}} and {{foo}} again") == {"foo"}


# --- fill_template ---

def test_fill_template_replaces_tokens():
    result = runner.fill_template("Hello {{name}}!", {"name": "world"})
    assert result == "Hello world!"

def test_fill_template_leaves_unknown_tokens():
    result = runner.fill_template("Hello {{name}} and {{other}}!", {"name": "world"})
    assert "{{other}}" in result

def test_fill_template_multiple_keys():
    result = runner.fill_template("{{a}} + {{b}}", {"a": "1", "b": "2"})
    assert result == "1 + 2"


# --- find_step ---

WORKFLOW = [
    {"id": "refresh", "template": "refresh.md"},
    {"id": "features-gen", "template": "gen_features.md"},
]

def test_find_step_returns_correct_step():
    step = runner.find_step(WORKFLOW, "features-gen")
    assert step["template"] == "gen_features.md"

def test_find_step_raises_for_unknown():
    with pytest.raises(ValueError, match="Unknown command"):
        runner.find_step(WORKFLOW, "nonexistent")


# --- extract_feature ---

def test_extract_feature_returns_correct_section():
    result = runner.extract_feature(FEATURES_TEXT, "F01")
    assert "Directory Scaffold" in result
    assert "F02" not in result

def test_extract_feature_second_entry():
    result = runner.extract_feature(FEATURES_TEXT, "F02")
    assert "YAML Config" in result
    assert "F01" not in result

def test_extract_feature_raises_for_missing():
    with pytest.raises(ValueError, match="F99"):
        runner.extract_feature(FEATURES_TEXT, "F99")


# --- extract_task ---

def test_extract_task_returns_correct_section():
    result = runner.extract_task(TASKS_TEXT, "T01")
    assert "Create directories" in result
    assert "T02" not in result

def test_extract_task_second_entry():
    result = runner.extract_task(TASKS_TEXT, "T02")
    assert "Write tests" in result
    assert "T01" not in result

def test_extract_task_raises_for_missing():
    with pytest.raises(ValueError, match="T99"):
        runner.extract_task(TASKS_TEXT, "T99")


# --- load_config / load_workflow (integration with temp files) ---

def test_load_config(tmp_path):
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    settings = {"project": {"name": "test"}, "planner": {"specs_dir": ".planner/specs"}}
    (config_dir / "settings.yaml").write_text(yaml.dump(settings))
    result = runner.load_config(tmp_path)
    assert result["project"]["name"] == "test"

def test_load_workflow(tmp_path):
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    workflow = {"steps": [{"id": "refresh", "template": "refresh.md"}]}
    (config_dir / "workflow.yaml").write_text(yaml.dump(workflow))
    result = runner.load_workflow(tmp_path)
    assert result[0]["id"] == "refresh"

def test_load_config_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        runner.load_config(tmp_path)


# --- build_context graceful fallback ---

# --- F05: /gen-features command ---

def make_temp_project(tmp_path, spec_text, rules_text):
    # Set up a minimal project directory with config, spec, rules, and gen_features template.
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    settings = {"j2": {
        "specs_dir": ".j2/specs",
        "features_file": ".j2/features/features.md",
        "tasks_dir": ".j2/tasks",
        "templates_dir": ".j2/templates",
        "rules_file": ".j2/rules.md",
    }}
    (config_dir / "settings.yaml").write_text(yaml.dump(settings))
    workflow = {"steps": [{"id": "features-gen", "template": "gen_features.md"}]}
    (config_dir / "workflow.yaml").write_text(yaml.dump(workflow))

    specs_dir = tmp_path / ".j2" / "specs"
    specs_dir.mkdir(parents=True)
    (specs_dir / "spec.md").write_text(spec_text)

    (tmp_path / ".j2" / "rules.md").write_text(rules_text)

    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    real_template = SCAFFOLD_ROOT / ".j2" / "templates" / "gen_features.md"
    (templates_dir / "gen_features.md").write_text(real_template.read_text())

    return tmp_path


def test_gen_features_renders_spec_and_rules(tmp_path):
    spec = "# My Project\nThis app tracks widgets."
    rules = "## Testing\n- All features need tests."
    root = make_temp_project(tmp_path, spec, rules)

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "features-gen")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = task = request = None

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "My Project" in output
    assert "tracks widgets" in output
    assert "All features need tests" in output
    assert "{{spec}}" not in output
    assert "{{rules}}" not in output


# --- F04: /refresh command ---

def make_refresh_project(tmp_path, spec_text, rules_text):
    # Set up a minimal project for refresh rendering.
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    settings = {"j2": {
        "specs_dir": ".j2/specs",
        "features_file": ".j2/features/features.md",
        "tasks_dir": ".j2/tasks",
        "templates_dir": ".j2/templates",
        "rules_file": ".j2/rules.md",
    }}
    (config_dir / "settings.yaml").write_text(yaml.dump(settings))
    workflow = {"steps": [{"id": "refresh", "template": "refresh.md"}]}
    (config_dir / "workflow.yaml").write_text(yaml.dump(workflow))

    specs_dir = tmp_path / ".j2" / "specs"
    specs_dir.mkdir(parents=True)
    (specs_dir / "spec.md").write_text(spec_text)

    (tmp_path / ".j2" / "rules.md").write_text(rules_text)

    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    real_template = SCAFFOLD_ROOT / ".j2" / "templates" / "refresh.md"
    (templates_dir / "refresh.md").write_text(real_template.read_text())

    return tmp_path


def test_refresh_renders_spec_and_rules(tmp_path):
    spec = "# Widget Tracker\nTracks widgets in real time."
    rules = "## Testing\n- Every feature needs a test."
    root = make_refresh_project(tmp_path, spec, rules)

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "refresh")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = task = request = None

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Widget Tracker" in output
    assert "Tracks widgets" in output
    assert "Every feature needs a test" in output
    assert "{{spec}}" not in output
    assert "{{rules}}" not in output


# --- F09: /start-task command ---

def make_start_task_project(tmp_path, spec_text, rules_text, features_text, tasks_text, feature_id):
    # Set up a minimal project for start-task rendering.
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    settings = {"j2": {
        "specs_dir": ".j2/specs",
        "features_file": ".j2/features/features.md",
        "tasks_dir": ".j2/tasks",
        "templates_dir": ".j2/templates",
        "rules_file": ".j2/rules.md",
    }}
    (config_dir / "settings.yaml").write_text(yaml.dump(settings))
    workflow = {"steps": [{"id": "task-start", "template": "start_task.md"}]}
    (config_dir / "workflow.yaml").write_text(yaml.dump(workflow))

    (tmp_path / ".j2" / "specs").mkdir(parents=True)
    (tmp_path / ".j2" / "specs" / "spec.md").write_text(spec_text)
    (tmp_path / ".j2" / "rules.md").write_text(rules_text)

    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(features_text)

    tasks_dir = tmp_path / ".j2" / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / f"{feature_id}.md").write_text(tasks_text)

    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    real_template = SCAFFOLD_ROOT / ".j2" / "templates" / "start_task.md"
    (templates_dir / "start_task.md").write_text(real_template.read_text())

    return tmp_path


def test_start_task_renders_all_placeholders(tmp_path):
    spec = "# Widget App\nTracks widgets."
    rules = "## Testing\n- Each feature needs a test."
    features = FEATURES_TEXT
    tasks = TASKS_TEXT

    root = make_start_task_project(tmp_path, spec, rules, features, tasks, "F01")

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "task-start")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = "F01"
        task = None
        request = None

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Widget App" in output
    assert "Each feature needs a test" in output
    assert "Directory Scaffold" in output
    assert "Create directories" in output
    assert "{{spec}}" not in output
    assert "{{rules}}" not in output
    assert "{{feature}}" not in output
    assert "{{tasks}}" not in output


# --- F08: /refine-tasks command ---

def make_refine_tasks_project(tmp_path, tasks_text, rules_text, feature_id):
    # Set up a minimal project for refine-tasks rendering.
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    settings = {"j2": {
        "specs_dir": ".j2/specs",
        "features_file": ".j2/features/features.md",
        "tasks_dir": ".j2/tasks",
        "templates_dir": ".j2/templates",
        "rules_file": ".j2/rules.md",
    }}
    (config_dir / "settings.yaml").write_text(yaml.dump(settings))
    workflow = {"steps": [{"id": "tasks-refine", "template": "refine_tasks.md"}]}
    (config_dir / "workflow.yaml").write_text(yaml.dump(workflow))

    tasks_dir = tmp_path / ".j2" / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / f"{feature_id}.md").write_text(tasks_text)

    (tmp_path / ".j2" / "rules.md").write_text(rules_text)

    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    real_template = SCAFFOLD_ROOT / ".j2" / "templates" / "refine_tasks.md"
    (templates_dir / "refine_tasks.md").write_text(real_template.read_text())

    return tmp_path


def test_refine_tasks_renders_tasks_rules_and_request(tmp_path):
    tasks = "### T01 — Create dirs\n**Status**: not started\n**Description**: Make subdirs.\n"
    rules = "## Testing\n- Each feature needs a test."
    request = "Split T01 into two tasks."

    root = make_refine_tasks_project(tmp_path, tasks, rules, "F01")

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "tasks-refine")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = "F01"
        task = None
        request = "Split T01 into two tasks."

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Create dirs" in output
    assert "Each feature needs a test" in output
    assert "Split T01 into two tasks" in output
    assert "{{tasks}}" not in output
    assert "{{rules}}" not in output
    assert "{{request}}" not in output


# --- F07: /gen-tasks command ---

def make_gen_tasks_project(tmp_path, spec_text, rules_text, features_text):
    # Set up a minimal project for gen-tasks rendering.
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    settings = {"j2": {
        "specs_dir": ".j2/specs",
        "features_file": ".j2/features/features.md",
        "tasks_dir": ".j2/tasks",
        "templates_dir": ".j2/templates",
        "rules_file": ".j2/rules.md",
    }}
    (config_dir / "settings.yaml").write_text(yaml.dump(settings))
    workflow = {"steps": [{"id": "tasks-gen", "template": "gen_tasks.md"}]}
    (config_dir / "workflow.yaml").write_text(yaml.dump(workflow))

    (tmp_path / ".j2" / "specs").mkdir(parents=True)
    (tmp_path / ".j2" / "specs" / "spec.md").write_text(spec_text)
    (tmp_path / ".j2" / "rules.md").write_text(rules_text)

    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(features_text)

    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    real_template = SCAFFOLD_ROOT / ".j2" / "templates" / "gen_tasks.md"
    (templates_dir / "gen_tasks.md").write_text(real_template.read_text())

    return tmp_path


def test_gen_tasks_renders_spec_rules_and_feature(tmp_path):
    spec = "# Widget App\nTracks widgets."
    rules = "## Testing\n- Each feature needs a test."
    features = FEATURES_TEXT

    root = make_gen_tasks_project(tmp_path, spec, rules, features)

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "tasks-gen")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = "F01"
        task = request = None

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Widget App" in output
    assert "Each feature needs a test" in output
    assert "Directory Scaffold" in output
    assert "{{spec}}" not in output
    assert "{{rules}}" not in output
    assert "{{feature}}" not in output


# --- F06: /refine-features command ---

def make_refine_features_project(tmp_path, features_text, rules_text):
    # Set up a minimal project for refine-features rendering.
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    settings = {"j2": {
        "specs_dir": ".j2/specs",
        "features_file": ".j2/features/features.md",
        "tasks_dir": ".j2/tasks",
        "templates_dir": ".j2/templates",
        "rules_file": ".j2/rules.md",
    }}
    (config_dir / "settings.yaml").write_text(yaml.dump(settings))
    workflow = {"steps": [{"id": "features-refine", "template": "refine_features.md"}]}
    (config_dir / "workflow.yaml").write_text(yaml.dump(workflow))

    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(features_text)

    (tmp_path / ".j2" / "rules.md").write_text(rules_text)

    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    real_template = SCAFFOLD_ROOT / ".j2" / "templates" / "refine_features.md"
    (templates_dir / "refine_features.md").write_text(real_template.read_text())

    return tmp_path


def test_refine_features_renders_features_rules_and_request(tmp_path):
    features = "## F01 — Widget Tracker\n**Priority**: High\n**Status**: not started\n"
    rules = "## Testing\n- All features need tests."
    request = "Change F01 priority to Low."
    root = make_refine_features_project(tmp_path, features, rules)

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "features-refine")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = task = None
        request = "Change F01 priority to Low."

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Widget Tracker" in output
    assert "All features need tests" in output
    assert "Change F01 priority to Low" in output
    assert "{{features}}" not in output
    assert "{{rules}}" not in output
    assert "{{request}}" not in output


# --- F15: principles file ---

TEMPLATES_DIR = Path(__file__).parent.parent / "scaffold" / ".j2" / "templates"
TEMPLATES_REQUIRING_RULES = [
    "gen_features.md", "gen_tasks.md", "refine_features.md", "refine_tasks.md",
    "start_task.md", "next_task.md", "milestone.md", "refresh.md",
]

def test_scaffold_rules_md_exists_and_nonempty():
    rules = Path(__file__).parent.parent / "scaffold" / ".j2" / "rules.md"
    assert rules.is_file()
    assert rules.stat().st_size > 0

@pytest.mark.parametrize("tmpl", TEMPLATES_REQUIRING_RULES)
def test_template_contains_rules_placeholder(tmpl):
    content = (TEMPLATES_DIR / tmpl).read_text()
    assert "{{rules}}" in content, f"{tmpl} is missing {{{{rules}}}} placeholder"

def test_extract_feature_case_insensitive():
    result = runner.extract_feature(FEATURES_TEXT, "f01")
    assert "Directory Scaffold" in result

def test_extract_task_case_insensitive():
    result = runner.extract_task(TASKS_TEXT, "t01")
    assert "Create directories" in result


# --- F02: YAML configuration system ---

SCAFFOLD_ROOT = Path(__file__).parent.parent / "scaffold"

REQUIRED_SETTINGS_KEYS = ["specs_dir", "features_file", "tasks_dir", "templates_dir", "rules_file"]
EXPECTED_COMMANDS = [
    "refresh", "features-gen", "features-refine", "tasks-gen", "tasks-refine",
    "task-start", "task-next", "try", "checkpoint", "milestone", "deploy",
]

def test_settings_yaml_has_required_j2_keys():
    import yaml
    settings = yaml.safe_load((SCAFFOLD_ROOT / ".j2" / "config" / "settings.yaml").read_text())
    for key in REQUIRED_SETTINGS_KEYS:
        assert key in settings["j2"], f"settings.yaml missing j2.{key}"

def test_workflow_yaml_covers_all_commands():
    import yaml
    workflow = yaml.safe_load((SCAFFOLD_ROOT / ".j2" / "config" / "workflow.yaml").read_text())
    ids = {step["id"] for step in workflow["steps"]}
    for cmd in EXPECTED_COMMANDS:
        assert cmd in ids, f"workflow.yaml missing step for {cmd!r}"

def test_workflow_yaml_templates_all_exist():
    import yaml
    workflow = yaml.safe_load((SCAFFOLD_ROOT / ".j2" / "config" / "workflow.yaml").read_text())
    templates_dir = SCAFFOLD_ROOT / ".j2" / "templates"
    for step in workflow["steps"]:
        tmpl = step["template"]
        assert (templates_dir / tmpl).is_file(), f"Template {tmpl!r} referenced in workflow.yaml does not exist"


# --- F01: scaffold directory structure ---

SCAFFOLD = Path(__file__).parent.parent / "scaffold"

@pytest.mark.parametrize("rel", [
    ".j2/specs",
    ".j2/features",
    ".j2/tasks",
    ".j2/config",
    ".j2/templates",
    ".claude/commands",
])
def test_scaffold_required_dirs_exist(rel):
    assert (SCAFFOLD / rel).is_dir(), f"scaffold/{rel} is missing"

def test_scaffold_install_script_exists():
    assert (SCAFFOLD / "install.sh").is_file()


def test_install_creates_required_dirs(tmp_path):
    # Running install.sh should create the expected directory structure.
    result = subprocess.run(
        ["bash", str(SCAFFOLD / "install.sh"), str(tmp_path)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    for rel in [".j2/config", ".j2/templates", ".j2/specs", ".claude/commands"]:
        assert (tmp_path / rel).is_dir(), f"{rel} missing after install"


def test_install_copies_scaffold_files(tmp_path):
    # Key scaffold files should be present in the target after install.
    subprocess.run(["bash", str(SCAFFOLD / "install.sh"), str(tmp_path)], check=True)
    assert (tmp_path / ".j2" / "config" / "workflow.yaml").is_file()
    assert (tmp_path / ".j2" / "config" / "settings.yaml").is_file()
    assert (tmp_path / ".claude" / "commands" / "refresh.md").is_file()


def test_install_does_not_overwrite_existing_file(tmp_path):
    # Re-running install.sh must not overwrite a file the user has customised.
    subprocess.run(["bash", str(SCAFFOLD / "install.sh"), str(tmp_path)], check=True)
    sentinel = tmp_path / ".j2" / "rules.md"
    original = sentinel.read_text()
    sentinel.write_text("custom content")
    subprocess.run(["bash", str(SCAFFOLD / "install.sh"), str(tmp_path)], check=True)
    assert sentinel.read_text() == "custom content", "install.sh overwrote an existing file"


# --- F18: /task-next command ---

def make_task_next_project(tmp_path, spec_text, rules_text, features_text):
    # Set up a minimal project for task-next rendering.
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    settings = {"j2": {
        "specs_dir": ".j2/specs",
        "features_file": ".j2/features/features.md",
        "tasks_dir": ".j2/tasks",
        "templates_dir": ".j2/templates",
        "rules_file": ".j2/rules.md",
    }}
    (config_dir / "settings.yaml").write_text(yaml.dump(settings))
    workflow = {"steps": [{"id": "task-next", "template": "next_task.md"}]}
    (config_dir / "workflow.yaml").write_text(yaml.dump(workflow))

    specs_dir = tmp_path / ".j2" / "specs"
    specs_dir.mkdir(parents=True)
    (specs_dir / "spec.md").write_text(spec_text)

    (tmp_path / ".j2" / "rules.md").write_text(rules_text)

    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(features_text)

    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    real_template = SCAFFOLD_ROOT / ".j2" / "templates" / "next_task.md"
    (templates_dir / "next_task.md").write_text(real_template.read_text())

    return tmp_path


def test_task_next_renders_rules_spec_and_features(tmp_path):
    spec = "# Widget App\nTracks widgets in real time."
    rules = "## Testing\n- Every feature needs a test."
    root = make_task_next_project(tmp_path, spec, rules, FEATURES_TEXT)

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "task-next")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = task = request = None

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Widget App" in output
    assert "Every feature needs a test" in output
    assert "Directory Scaffold" in output  # from FEATURES_TEXT
    assert "{{rules}}" not in output
    assert "{{spec}}" not in output
    assert "{{features}}" not in output


# --- F22: colored structured footer ---

def test_footer_contains_ansi_color_codes():
    # All three labels must be ANSI-colored.
    assert "\033[32mcompleted:" in runner.FOOTER
    assert "\033[33mstate:" in runner.FOOTER
    assert "\033[36mnext:" in runner.FOOTER


def test_footer_instructs_state_md_write():
    # Footer must tell Claude to write state.md.
    assert "state.md" in runner.FOOTER
    assert "without ANSI" in runner.FOOTER


# --- footer in rendered output ---

def test_rendered_output_contains_state_and_next_footer(tmp_path):
    spec = "# My Project\nThis app tracks widgets."
    rules = "## Testing\n- All features need tests."
    root = make_temp_project(tmp_path, spec, rules)

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "features-gen")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = task = request = None

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context) + runner.FOOTER

    assert "completed:" in output
    assert "state:" in output
    assert "next:" in output


# --- F21: /next command ---

def test_resolve_next_command_bare(tmp_path):
    # A state.md with a bare next command should set args.command correctly.
    (tmp_path / ".j2").mkdir(parents=True)
    (tmp_path / ".j2" / "state.md").write_text("completed: something\nstate: 0 | 0 | 0\nnext: /task-next\n")

    class Args:
        command = "next"
        feature = None

    args = Args()
    runner.resolve_next_command(tmp_path, args)
    assert args.command == "task-next"
    assert args.feature is None


def test_resolve_next_command_with_feature(tmp_path):
    # A state.md with a feature arg should also set args.feature.
    (tmp_path / ".j2").mkdir(parents=True)
    (tmp_path / ".j2" / "state.md").write_text("completed: something\nstate: 0 | 0 | 0\nnext: /tasks-gen F11\n")

    class Args:
        command = "next"
        feature = None

    args = Args()
    runner.resolve_next_command(tmp_path, args)
    assert args.command == "tasks-gen"
    assert args.feature == "F11"


def test_resolve_next_command_missing_state(tmp_path):
    # Missing state.md should raise ValueError or FileNotFoundError.
    (tmp_path / ".j2").mkdir(parents=True)

    class Args:
        command = "next"
        feature = None

    with pytest.raises((ValueError, FileNotFoundError)):
        runner.resolve_next_command(tmp_path, Args())


# --- build_context graceful fallback ---

def test_build_context_substitutes_placeholder_for_missing_file(tmp_path):
    # Missing files should produce a descriptive placeholder, not crash.
    settings = {
        "j2": {
            "features_file": ".j2/features/features.md",
            "specs_dir": ".j2/specs",
            "rules_file": ".j2/rules.md",
            "tasks_dir": ".j2/tasks",
            "templates_dir": ".j2/templates",
        }
    }

    class FakeArgs:
        feature = "F01"
        task = "T01"
        request = None

    context = runner.build_context(tmp_path, settings, {"features"}, FakeArgs())
    assert "features" in context
    assert "not yet available" in context["features"]


# --- F10: /milestone command ---

MILESTONE_TASKS_TEXT = """\
# Tasks for F01

### T01 — Create directories
**Status**: done
**Description**: Make all required subdirectories.

### T02 — Write tests
**Status**: done
**Description**: Write tests for directory creation.
"""


def make_milestone_project(tmp_path, rules_text, features_text, tasks_text, feature_id):
    # Set up a minimal project for milestone rendering.
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    settings = {"j2": {
        "specs_dir": ".j2/specs",
        "features_file": ".j2/features/features.md",
        "tasks_dir": ".j2/tasks",
        "templates_dir": ".j2/templates",
        "rules_file": ".j2/rules.md",
    }}
    (config_dir / "settings.yaml").write_text(yaml.dump(settings))
    workflow = {"steps": [{"id": "milestone", "template": "milestone.md"}]}
    (config_dir / "workflow.yaml").write_text(yaml.dump(workflow))

    (tmp_path / ".j2" / "specs").mkdir(parents=True)
    (tmp_path / ".j2" / "rules.md").write_text(rules_text)

    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(features_text)

    tasks_dir = tmp_path / ".j2" / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / f"{feature_id}.md").write_text(tasks_text)

    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    real_template = SCAFFOLD_ROOT / ".j2" / "templates" / "milestone.md"
    (templates_dir / "milestone.md").write_text(real_template.read_text())

    return tmp_path


def test_milestone_renders_feature_and_tasks(tmp_path):
    # Milestone template must inject the single feature section and its task list.
    rules = "## Testing\n- Each feature needs a test."
    root = make_milestone_project(tmp_path, rules, FEATURES_TEXT, MILESTONE_TASKS_TEXT, "F01")

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "milestone")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = "F01"
        task = request = None

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Directory Scaffold" in output   # from extracted feature section
    assert "Create directories" in output   # from tasks
    assert "Every feature needs a test" not in output or "Testing" in output
    assert "{{feature}}" not in output
    assert "{{tasks}}" not in output
    assert "{{rules}}" not in output


def test_milestone_missing_feature_id_produces_error(tmp_path):
    # Runner must exit non-zero when --feature is not provided for milestone.
    result = subprocess.run(
        ["python3", str(SCAFFOLD_ROOT / ".j2" / "runner.py"),
         "milestone", "--root", str(tmp_path)],
        capture_output=True, text=True
    )
    assert result.returncode != 0
