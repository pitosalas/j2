"""Tests for scaffold/.j2/runner.py"""

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
    {"id": "spec-review", "template": "spec_review.md"},
    {"id": "gen-features", "template": "gen_features.md"},
]

def test_find_step_returns_correct_step():
    step = runner.find_step(WORKFLOW, "gen-features")
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
    workflow = {"steps": [{"id": "spec-review", "template": "spec_review.md"}]}
    (config_dir / "workflow.yaml").write_text(yaml.dump(workflow))
    result = runner.load_workflow(tmp_path)
    assert result[0]["id"] == "spec-review"

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
    workflow = {"steps": [{"id": "gen-features", "template": "gen_features.md"}]}
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
    step = runner.find_step(workflow, "gen-features")
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
    workflow = {"steps": [{"id": "start-task", "template": "start_task.md"}]}
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
    step = runner.find_step(workflow, "start-task")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = "F01"
        task = "T01"
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
    assert "{{task}}" not in output


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
    workflow = {"steps": [{"id": "refine-tasks", "template": "refine_tasks.md"}]}
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
    step = runner.find_step(workflow, "refine-tasks")
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
    workflow = {"steps": [{"id": "gen-tasks", "template": "gen_tasks.md"}]}
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
    step = runner.find_step(workflow, "gen-tasks")
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
    workflow = {"steps": [{"id": "refine-features", "template": "refine_features.md"}]}
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
    step = runner.find_step(workflow, "refine-features")
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
    "start_task.md", "next_task.md", "milestone.md", "spec_review.md",
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
    "spec-review", "gen-features", "refine-features", "gen-tasks", "refine-tasks",
    "start-task", "next-task", "try", "checkpoint", "milestone",
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
