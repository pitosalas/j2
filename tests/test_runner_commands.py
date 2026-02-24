#!/usr/bin/env python3
"""Tests for command template rendering: features-gen, refresh, task-start, tasks-update, tasks-gen, features-update, task-next."""
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

from pathlib import Path

import runner
import yaml

from conftest import CONFIG_ROOT, FEATURES_TEXT, TASKS_TEXT, TEMPLATES_ROOT


def _base_settings():
    return {"j2": {
        "specs_dir": ".j2/specs",
        "features_file": ".j2/features/features.md",
        "tasks_dir": ".j2/tasks",
        "templates_dir": ".j2/templates",
        "rules_file": ".j2/rules.md",
    }}


# --- F05: /features-gen command ---

def make_temp_project(tmp_path, spec_text, rules_text):
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "settings.yaml").write_text(yaml.dump(_base_settings()))
    (config_dir / "workflow.yaml").write_text(yaml.dump(
        {"steps": [{"id": "features-gen", "template": "gen_features.md"}]}
    ))
    specs_dir = tmp_path / ".j2" / "specs"
    specs_dir.mkdir(parents=True)
    (specs_dir / "spec.md").write_text(spec_text)
    (tmp_path / ".j2" / "rules.md").write_text(rules_text)
    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "gen_features.md").write_text((TEMPLATES_ROOT / "gen_features.md").read_text())
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
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "settings.yaml").write_text(yaml.dump(_base_settings()))
    (config_dir / "workflow.yaml").write_text(yaml.dump(
        {"steps": [{"id": "refresh", "template": "refresh.md"}]}
    ))
    specs_dir = tmp_path / ".j2" / "specs"
    specs_dir.mkdir(parents=True)
    (specs_dir / "spec.md").write_text(spec_text)
    (tmp_path / ".j2" / "rules.md").write_text(rules_text)
    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "refresh.md").write_text((TEMPLATES_ROOT / "refresh.md").read_text())
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


# --- F09: /task-start command ---

def make_start_task_project(tmp_path, spec_text, rules_text, features_text, tasks_text, feature_id):
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "settings.yaml").write_text(yaml.dump(_base_settings()))
    (config_dir / "workflow.yaml").write_text(yaml.dump(
        {"steps": [{"id": "task-start", "template": "start_task.md"}]}
    ))
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
    (templates_dir / "start_task.md").write_text((TEMPLATES_ROOT / "start_task.md").read_text())
    return tmp_path


def test_start_task_renders_all_placeholders(tmp_path):
    spec = "# Widget App\nTracks widgets."
    rules = "## Testing\n- Each feature needs a test."
    root = make_start_task_project(tmp_path, spec, rules, FEATURES_TEXT, TASKS_TEXT, "F01")

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "task-start")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = "F01"
        task = request = target = None

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Each feature needs a test" in output
    assert "{{rules}}" not in output
    # spec and features no longer injected into start_task template (F30)
    assert "{{spec}}" not in output
    assert "{{features}}" not in output


# --- F08: /tasks-update command ---

def make_update_tasks_project(tmp_path, tasks_text, rules_text, feature_id):
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "settings.yaml").write_text(yaml.dump(_base_settings()))
    (config_dir / "workflow.yaml").write_text(yaml.dump(
        {"steps": [{"id": "tasks-update", "template": "update_tasks.md"}]}
    ))
    tasks_dir = tmp_path / ".j2" / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / f"{feature_id}.md").write_text(tasks_text)
    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(FEATURES_TEXT)
    (tmp_path / ".j2" / "rules.md").write_text(rules_text)
    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "update_tasks.md").write_text((TEMPLATES_ROOT / "update_tasks.md").read_text())
    return tmp_path


def test_update_tasks_renders_tasks_rules_and_request(tmp_path):
    tasks = "### T01 — Create dirs\n**Status**: not started\n**Description**: Make subdirs.\n"
    rules = "## Testing\n- Each feature needs a test."
    root = make_update_tasks_project(tmp_path, tasks, rules, "F01")

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "tasks-update")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = "F01"
        task = None
        request = "Split T01 into two tasks."

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Directory Scaffold" in output
    assert "Each feature needs a test" in output
    assert "{{features}}" not in output
    assert "{{rules}}" not in output


# --- F07: /tasks-gen command ---

def make_gen_tasks_project(tmp_path, spec_text, rules_text, features_text):
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "settings.yaml").write_text(yaml.dump(_base_settings()))
    (config_dir / "workflow.yaml").write_text(yaml.dump(
        {"steps": [{"id": "tasks-gen", "template": "gen_tasks.md"}]}
    ))
    (tmp_path / ".j2" / "specs").mkdir(parents=True)
    (tmp_path / ".j2" / "specs" / "spec.md").write_text(spec_text)
    (tmp_path / ".j2" / "rules.md").write_text(rules_text)
    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(features_text)
    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "gen_tasks.md").write_text((TEMPLATES_ROOT / "gen_tasks.md").read_text())
    return tmp_path


def test_gen_tasks_renders_spec_rules_and_feature(tmp_path):
    spec = "# Widget App\nTracks widgets."
    rules = "## Testing\n- Each feature needs a test."
    root = make_gen_tasks_project(tmp_path, spec, rules, FEATURES_TEXT)

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


# --- F06: /features-update command ---

def make_update_features_project(tmp_path, features_text, rules_text):
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "settings.yaml").write_text(yaml.dump(_base_settings()))
    (config_dir / "workflow.yaml").write_text(yaml.dump(
        {"steps": [{"id": "features-update", "template": "update_features.md"}]}
    ))
    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(features_text)
    (tmp_path / ".j2" / "rules.md").write_text(rules_text)
    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "update_features.md").write_text((TEMPLATES_ROOT / "update_features.md").read_text())
    return tmp_path


def test_update_features_renders_features_rules_and_request(tmp_path):
    features = "## F01 — Widget Tracker\n**Priority**: High\n**Status**: not started\n"
    rules = "## Testing\n- All features need tests."
    root = make_update_features_project(tmp_path, features, rules)

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "features-update")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = task = None
        request = "Change F01 priority to Low."

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Widget Tracker" in output
    assert "All features need tests" in output
    assert "{{features}}" not in output
    assert "{{rules}}" not in output


# --- F18: /task-next command ---

def make_task_next_project(tmp_path, spec_text, rules_text, features_text):
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "settings.yaml").write_text(yaml.dump(_base_settings()))
    (config_dir / "workflow.yaml").write_text(yaml.dump(
        {"steps": [{"id": "task-next", "template": "next_task.md"}]}
    ))
    specs_dir = tmp_path / ".j2" / "specs"
    specs_dir.mkdir(parents=True)
    (specs_dir / "spec.md").write_text(spec_text)
    (tmp_path / ".j2" / "rules.md").write_text(rules_text)
    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(features_text)
    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "next_task.md").write_text((TEMPLATES_ROOT / "next_task.md").read_text())
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

    assert "Every feature needs a test" in output
    assert "{{rules}}" not in output
    # spec and features no longer injected into next_task template (F30)
    assert "{{spec}}" not in output
    assert "{{features}}" not in output


# --- F32: /task-run-all command ---

def test_run_all_tasks_template_has_correct_placeholders():
    template = (TEMPLATES_ROOT / "run_all_tasks.md").read_text()
    assert "{{feature_id}}" in template
    assert "{{rules}}" in template
    assert "{{spec}}" not in template
    assert "{{features}}" not in template


def test_run_all_tasks_workflow_entry_exists():
    workflow = yaml.safe_load((CONFIG_ROOT / "workflow.yaml").read_text())
    step_ids = [s["id"] for s in workflow["steps"]]
    assert "task-run-all" in step_ids
    step = next(s for s in workflow["steps"] if s["id"] == "task-run-all")
    assert step["template"] == "run_all_tasks.md"


def test_run_all_tasks_slash_command_exists():
    cmd_path = Path(__file__).parent.parent / ".claude" / "commands" / "task-run-all.md"
    assert cmd_path.exists()
    content = cmd_path.read_text()
    assert "runner.py task-run-all" in content
    assert "$ARGUMENTS" in content


# --- F33: /features-parallel command ---

def test_features_parallel_template_has_correct_placeholders():
    template = (TEMPLATES_ROOT / "features_parallel.md").read_text()
    assert "{{features}}" in template
    assert "{{rules}}" in template
    assert "{{spec}}" not in template


def test_features_parallel_workflow_entry_exists():
    workflow = yaml.safe_load((CONFIG_ROOT / "workflow.yaml").read_text())
    step_ids = [s["id"] for s in workflow["steps"]]
    assert "features-parallel" in step_ids
    step = next(s for s in workflow["steps"] if s["id"] == "features-parallel")
    assert step["template"] == "features_parallel.md"


def test_features_parallel_slash_command_exists():
    cmd_path = Path(__file__).parent.parent / ".claude" / "commands" / "features-parallel.md"
    assert cmd_path.exists()
    content = cmd_path.read_text()
    assert "runner.py features-parallel" in content


# --- F36: /features-update auto-task-gen and two-section invariant ---

def test_update_features_template_contains_auto_task_gen():
    template = (TEMPLATES_ROOT / "update_features.md").read_text()
    assert "newly added" in template
    assert "task file" in template

def test_update_features_template_contains_two_section_invariant():
    template = (TEMPLATES_ROOT / "update_features.md").read_text()
    assert "incomplete" in template.lower()
    assert "completed" in template.lower()
    assert "two-section" in template.lower() or "two section" in template.lower()


# --- F37: workflow principle guards in templates ---

def test_start_task_template_has_missing_file_guard():
    template = (TEMPLATES_ROOT / "start_task.md").read_text()
    assert "does not exist" in template
    assert "Error:" in template

def test_next_task_template_has_missing_file_guard():
    template = (TEMPLATES_ROOT / "next_task.md").read_text()
    assert "does not exist" in template
    assert "Error:" in template

def test_run_all_tasks_template_has_missing_file_guard():
    template = (TEMPLATES_ROOT / "run_all_tasks.md").read_text()
    assert "does not exist" in template
    assert "Error:" in template

def test_gen_tasks_template_has_feature_guard():
    template = (TEMPLATES_ROOT / "gen_tasks.md").read_text()
    assert "not yet available" in template
    assert "Error:" in template

def test_checkpoint_template_skips_commit_when_nothing_staged():
    template = (TEMPLATES_ROOT / "checkpoint.md").read_text()
    assert "empty" in template or "nothing staged" in template or "No changes" in template
