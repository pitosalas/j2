#!/usr/bin/env python3
"""Tests for scaffold/config/install: F15 rules, F02 YAML config, F01 scaffold dirs, F12 arg patterns, F14 ROS2, F19 deploy, F26 code-review."""
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

import subprocess
from pathlib import Path

import pytest
import runner
import yaml

from conftest import CONFIG_ROOT, FEATURES_TEXT, SCAFFOLD, SCAFFOLD_ROOT, SETTINGS_FOR_F23, TEMPLATES_ROOT


J2_ROOT = Path(__file__).parent.parent / ".j2"


# --- F15: principles file ---

TEMPLATES_DIR = Path(__file__).parent.parent / ".j2" / "templates"
TEMPLATES_REQUIRING_RULES = [
    "gen_features.md", "gen_tasks.md", "update_features.md", "update_tasks.md",
    "start_task.md", "next_task.md", "milestone.md", "refresh.md", "code_review.md",
]

def test_scaffold_rules_md_exists_and_nonempty():
    rules = Path(__file__).parent.parent / "scaffold" / ".j2" / "rules.md"
    assert rules.is_file()
    assert rules.stat().st_size > 0

@pytest.mark.parametrize("tmpl", TEMPLATES_REQUIRING_RULES)
def test_template_contains_rules_placeholder(tmpl):
    content = (TEMPLATES_DIR / tmpl).read_text()
    assert "{{rules}}" in content, f"{tmpl} is missing {{{{rules}}}} placeholder"


# --- F02: YAML configuration system ---

REQUIRED_SETTINGS_KEYS = ["specs_dir", "features_file", "tasks_dir", "templates_dir", "rules_file"]
EXPECTED_COMMANDS = [
    "refresh", "features-gen", "features-update", "tasks-gen", "tasks-update",
    "task-start", "task-next", "checkpoint", "milestone", "deploy",
]

def test_settings_yaml_has_required_j2_keys():
    settings = yaml.safe_load((CONFIG_ROOT / "settings.yaml").read_text())
    for key in REQUIRED_SETTINGS_KEYS:
        assert key in settings["j2"], f"settings.yaml missing j2.{key}"

def test_workflow_yaml_covers_all_commands():
    workflow = yaml.safe_load((CONFIG_ROOT / "workflow.yaml").read_text())
    ids = {step["id"] for step in workflow["steps"]}
    for cmd in EXPECTED_COMMANDS:
        assert cmd in ids, f"workflow.yaml missing step for {cmd!r}"

def test_workflow_yaml_templates_all_exist():
    workflow = yaml.safe_load((CONFIG_ROOT / "workflow.yaml").read_text())
    for step in workflow["steps"]:
        tmpl = step["template"]
        assert (TEMPLATES_ROOT / tmpl).is_file(), f"Template {tmpl!r} referenced in workflow.yaml does not exist"


# --- F01: scaffold directory structure ---

@pytest.mark.parametrize("rel", [
    ".j2/specs",
    ".j2/features",
    ".j2/tasks",
    ".claude/commands",
])
def test_scaffold_required_dirs_exist(rel):
    assert (SCAFFOLD / rel).is_dir(), f"scaffold/{rel} is missing"

def test_scaffold_install_script_exists():
    assert (SCAFFOLD / "install.sh").is_file()

def test_install_creates_required_dirs(tmp_path):
    result = subprocess.run(
        ["bash", str(SCAFFOLD / "install.sh"), str(tmp_path)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    for rel in [".j2/config", ".j2/templates", ".j2/specs", ".claude/commands"]:
        assert (tmp_path / rel).is_dir(), f"{rel} missing after install"

def test_install_copies_scaffold_files(tmp_path):
    subprocess.run(["bash", str(SCAFFOLD / "install.sh"), str(tmp_path)], check=True)
    assert (tmp_path / ".j2" / "config" / "workflow.yaml").is_file()
    assert (tmp_path / ".j2" / "config" / "settings.yaml").is_file()
    assert (tmp_path / ".claude" / "commands" / "refresh.md").is_file()

def test_install_does_not_overwrite_existing_file(tmp_path):
    subprocess.run(["bash", str(SCAFFOLD / "install.sh"), str(tmp_path)], check=True)
    sentinel = tmp_path / ".j2" / "rules.md"
    sentinel.write_text("custom content")
    subprocess.run(["bash", str(SCAFFOLD / "install.sh"), str(tmp_path)], check=True)
    assert sentinel.read_text() == "custom content", "install.sh overwrote an existing file"


# --- F24: tasks/done scaffold ---

def test_scaffold_tasks_done_dir_exists():
    assert (SCAFFOLD / ".j2" / "tasks" / "done").is_dir()

def test_install_creates_tasks_done_dir(tmp_path):
    result = subprocess.run(
        ["bash", str(SCAFFOLD / "install.sh"), str(tmp_path)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / ".j2" / "tasks" / "done").is_dir()


# --- F12: inline argument pattern ---

INTERACTIVE_PROMPT_TEMPLATES = [
    "update_features.md",
    "update_tasks.md",
]

@pytest.mark.parametrize("tmpl", INTERACTIVE_PROMPT_TEMPLATES)
def test_interactive_prompt_template_contains_stop_and_wait(tmpl):
    content = (TEMPLATES_ROOT / tmpl).read_text()
    assert "stop and wait" in content.lower(), f"{tmpl} missing 'stop and wait' instruction"

INLINE_ARG_TEMPLATES = [
    "gen_tasks.md",
    "start_task.md",
    "milestone.md",
]

@pytest.mark.parametrize("tmpl", INLINE_ARG_TEMPLATES)
def test_inline_arg_template_uses_feature_id_placeholder(tmpl):
    content = (TEMPLATES_ROOT / tmpl).read_text()
    assert "{{feature_id}}" in content, f"{tmpl} missing {{{{feature_id}}}} placeholder"

@pytest.mark.parametrize("tmpl", ["update_tasks.md", "gen_tasks.md"])
def test_template_uses_features_placeholder(tmpl):
    content = (TEMPLATES_ROOT / tmpl).read_text()
    assert "{{features}}" in content, f"{tmpl} missing {{{{features}}}} placeholder"

def test_feature_id_injected_from_feature_arg(tmp_path):
    (tmp_path / ".j2" / "features").mkdir(parents=True)
    (tmp_path / ".j2" / "features" / "features.md").write_text(FEATURES_TEXT)

    class Args:
        feature = "F01"
        task = request = target = None

    context = runner.build_context(tmp_path, SETTINGS_FOR_F23, {"feature_id"}, Args())
    assert context["feature_id"] == "F01"

def test_feature_id_falls_back_to_default_when_arg_omitted(tmp_path):
    (tmp_path / ".j2" / "features").mkdir(parents=True)
    (tmp_path / ".j2" / "features" / "features.md").write_text(FEATURES_TEXT)

    class Args:
        feature = None
        task = request = target = None

    context = runner.build_context(tmp_path, SETTINGS_FOR_F23, {"feature_id"}, Args())
    assert context["feature_id"] == "F01"

def test_target_injected_when_target_arg_provided(tmp_path):
    class Args:
        feature = task = request = None
        target = "../my-project"

    context = runner.build_context(tmp_path, SETTINGS_FOR_F23, {"target"}, Args())
    assert context["target"] == "../my-project"

def test_request_injected_when_request_arg_provided(tmp_path):
    class Args:
        feature = task = target = None
        request = "Split T01 into two tasks."

    context = runner.build_context(tmp_path, SETTINGS_FOR_F23, {"request"}, Args())
    assert context["request"] == "Split T01 into two tasks."


# --- F14: ROS2 configuration profile ---

def test_ros2_settings_yaml_is_valid_and_has_required_keys():
    path = CONFIG_ROOT / "settings.ros2.yaml"
    assert path.is_file(), "settings.ros2.yaml not found in .j2/config/"
    data = yaml.safe_load(path.read_text())
    assert data["project"]["platform"] == "ros2"
    assert "package_type" in data["ros2"]
    assert "node_type" in data["ros2"]

@pytest.mark.parametrize("tmpl", ["gen_features.ros2.md", "gen_tasks.ros2.md"])
def test_ros2_templates_exist_and_load(tmpl):
    path = TEMPLATES_ROOT / tmpl
    assert path.is_file(), f"{tmpl} not found in .j2/templates/"
    assert len(path.read_text()) > 0

@pytest.mark.parametrize("tmpl", ["gen_features.ros2.md", "gen_tasks.ros2.md"])
def test_ros2_templates_contain_ros2_guidance(tmpl):
    content = (TEMPLATES_ROOT / tmpl).read_text().lower()
    assert "ros2" in content
    assert "rclpy" in content or "rclcpp" in content


# --- F19: /deploy command ---

def make_deploy_project(tmp_path):
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
    (config_dir / "workflow.yaml").write_text(yaml.dump(
        {"steps": [{"id": "deploy", "template": "deploy.md"}]}
    ))
    (tmp_path / ".j2" / "rules.md").write_text("## Rules\n- Write tests.\n")
    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "deploy.md").write_text((TEMPLATES_ROOT / "deploy.md").read_text())
    return tmp_path


def test_deploy_renders_with_provided_target(tmp_path):
    root = make_deploy_project(tmp_path)

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "deploy")
    template = runner.load_template(root, settings, step["template"])

    class Args:
        feature = task = request = None
        target = "../my-project"

    placeholders = runner.find_placeholders(template)
    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "../my-project" in output
    assert "mkdir" in output
    assert "install.sh" in output


# --- F26: /code-review command ---

def make_code_review_project(tmp_path, rules_text):
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
    (config_dir / "workflow.yaml").write_text(yaml.dump(
        {"steps": [{"id": "code-review", "template": "code_review.md"}]}
    ))
    (tmp_path / ".j2" / "rules.md").write_text(rules_text)
    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "code_review.md").write_text((TEMPLATES_ROOT / "code_review.md").read_text())
    return tmp_path


def test_code_review_renders_rules(tmp_path):
    rules = "## Testing\n- Each feature must have at least one test.\n"
    root = make_code_review_project(tmp_path, rules)

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "code-review")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = task = request = target = None

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Each feature must have at least one test" in output
    assert "{{rules}}" not in output

def test_code_review_workflow_registered():
    workflow = yaml.safe_load((CONFIG_ROOT / "workflow.yaml").read_text())
    ids = {s["id"]: s for s in workflow["steps"]}
    assert "code-review" in ids
    assert ids["code-review"]["template"] == "code_review.md"


# --- milestone: runner exits non-zero when --feature missing ---

def test_milestone_missing_feature_id_produces_error(tmp_path):
    result = subprocess.run(
        ["python3", str(J2_ROOT / "runner.py"), "milestone", "--root", str(tmp_path)],
        capture_output=True, text=True
    )
    assert result.returncode != 0
