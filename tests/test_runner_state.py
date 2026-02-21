#!/usr/bin/env python3
"""Tests for state management: footer, /continue, /milestone, F23 workflow order, F24 archive, F16 checkpoint."""
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

from pathlib import Path

import pytest
import runner
import yaml

from conftest import FEATURES_TEXT, MILESTONE_TASKS_TEXT, MIXED_PRIORITY_FEATURES, SETTINGS_FOR_F23, TEMPLATES_ROOT


def _base_settings():
    return {"j2": {
        "specs_dir": ".j2/specs",
        "features_file": ".j2/features/features.md",
        "tasks_dir": ".j2/tasks",
        "templates_dir": ".j2/templates",
        "rules_file": ".j2/rules.md",
    }}


# --- F22: colored structured footer ---

def test_footer_contains_ansi_color_codes():
    assert "\033[32mcompleted:" in runner.FOOTER
    assert "\033[33mstate:" in runner.FOOTER
    assert "\033[36mnext:" in runner.FOOTER

def test_footer_instructs_state_md_write():
    assert "state.md" in runner.FOOTER
    assert "without ANSI" in runner.FOOTER

def test_footer_contains_ordering_instructions():
    assert "spec gaps" in runner.FOOTER
    assert "task files" in runner.FOOTER or "missing_tasks" in runner.FOOTER or "tasks-gen" in runner.FOOTER
    assert "task-next" in runner.FOOTER


# --- footer in rendered output ---

def test_rendered_output_contains_state_and_next_footer(tmp_path):
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "settings.yaml").write_text(yaml.dump(_base_settings()))
    (config_dir / "workflow.yaml").write_text(yaml.dump(
        {"steps": [{"id": "features-gen", "template": "gen_features.md"}]}
    ))
    specs_dir = tmp_path / ".j2" / "specs"
    specs_dir.mkdir(parents=True)
    (specs_dir / "spec.md").write_text("# My Project\nThis app tracks widgets.")
    (tmp_path / ".j2" / "rules.md").write_text("## Testing\n- All features need tests.")
    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "gen_features.md").write_text((TEMPLATES_ROOT / "gen_features.md").read_text())

    settings = runner.load_config(tmp_path)
    workflow = runner.load_workflow(tmp_path)
    step = runner.find_step(workflow, "features-gen")
    template = runner.load_template(tmp_path, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = task = request = None

    context = runner.build_context(tmp_path, settings, placeholders, Args())
    output = runner.fill_template(template, context) + runner.FOOTER

    assert "completed:" in output
    assert "state:" in output
    assert "next:" in output


# --- F21: /continue command ---

def test_resolve_next_command_bare(tmp_path):
    (tmp_path / ".j2").mkdir(parents=True)
    (tmp_path / ".j2" / "state.md").write_text("completed: something\nstate: 0 | 0 | 0\nnext: /task-next\n")

    class Args:
        command = "continue"
        feature = None

    args = Args()
    runner.resolve_next_command(tmp_path, args)
    assert args.command == "task-next"
    assert args.feature is None

def test_resolve_next_command_with_feature(tmp_path):
    (tmp_path / ".j2").mkdir(parents=True)
    (tmp_path / ".j2" / "state.md").write_text("completed: something\nstate: 0 | 0 | 0\nnext: /tasks-gen F11\n")

    class Args:
        command = "continue"
        feature = None

    args = Args()
    runner.resolve_next_command(tmp_path, args)
    assert args.command == "tasks-gen"
    assert args.feature == "F11"

def test_resolve_next_command_missing_state(tmp_path):
    (tmp_path / ".j2").mkdir(parents=True)

    class Args:
        command = "continue"
        feature = None

    with pytest.raises((ValueError, FileNotFoundError)):
        runner.resolve_next_command(tmp_path, Args())


# --- F10: /milestone command ---

def make_milestone_project(tmp_path, rules_text, features_text, tasks_text, feature_id):
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "settings.yaml").write_text(yaml.dump(_base_settings()))
    (config_dir / "workflow.yaml").write_text(yaml.dump(
        {"steps": [{"id": "milestone", "template": "milestone.md"}]}
    ))
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
    (templates_dir / "milestone.md").write_text((TEMPLATES_ROOT / "milestone.md").read_text())
    return tmp_path


def test_milestone_renders_feature_and_tasks(tmp_path):
    rules = "## Testing\n- Each feature needs a test."
    root = make_milestone_project(tmp_path, rules, FEATURES_TEXT, MILESTONE_TASKS_TEXT, "F01")

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "milestone")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = "F01"
        task = request = target = None

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Directory Scaffold" in output
    assert "Create directories" in output
    assert "Each feature needs a test" in output
    assert "{{feature}}" not in output
    assert "{{tasks}}" not in output
    assert "{{rules}}" not in output

def test_milestone_template_instructs_readme_update():
    content = (TEMPLATES_ROOT / "milestone.md").read_text()
    assert "readme" in content.lower()
    assert "rewrite" in content.lower() or "update" in content.lower()

def test_milestone_renders_feature_id(tmp_path):
    rules = "## Testing\n- Each feature needs a test."
    root = make_milestone_project(tmp_path, rules, FEATURES_TEXT, MILESTONE_TASKS_TEXT, "F01")

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "milestone")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = "F01"
        task = request = target = None

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "{{feature_id}}" not in output
    assert "F01" in output

def test_milestone_template_instructs_feature_reorder():
    content = (TEMPLATES_ROOT / "milestone.md").read_text()
    assert "completed section" in content.lower()
    assert "incomplete section" in content.lower() or "incomplete features" in content.lower()


# --- F23: workflow-ordered next step logic ---

def test_missing_tasks_summary_sorted_by_priority(tmp_path):
    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(MIXED_PRIORITY_FEATURES)
    (tmp_path / ".j2" / "tasks").mkdir(parents=True)

    result = runner.missing_tasks_summary(tmp_path, SETTINGS_FOR_F23)

    assert result != "none"
    assert result.index("F02") < result.index("F03") < result.index("F01")

def test_missing_tasks_summary_excludes_feature_with_task_file(tmp_path):
    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(MIXED_PRIORITY_FEATURES)
    tasks_dir = tmp_path / ".j2" / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "F02.md").write_text("# Tasks for F02\n### T01 — stub\n")

    result = runner.missing_tasks_summary(tmp_path, SETTINGS_FOR_F23)

    assert "F02" not in result
    assert "F01" in result or "F03" in result

def test_missing_tasks_summary_excludes_done_features(tmp_path):
    features = """\
## F01 — Done Feature
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Already done.

---
"""
    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(features)
    (tmp_path / ".j2" / "tasks").mkdir(parents=True)

    result = runner.missing_tasks_summary(tmp_path, SETTINGS_FOR_F23)
    assert result == "none"

def test_missing_tasks_summary_returns_none_when_all_have_task_files(tmp_path):
    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(MIXED_PRIORITY_FEATURES)
    tasks_dir = tmp_path / ".j2" / "tasks"
    tasks_dir.mkdir(parents=True)
    for fid in ("F01", "F02", "F03"):
        (tasks_dir / f"{fid}.md").write_text(f"# Tasks for {fid}\n")

    result = runner.missing_tasks_summary(tmp_path, SETTINGS_FOR_F23)
    assert result == "none"


# --- F24: completed tasks archive ---

def test_missing_tasks_summary_excludes_archived_feature(tmp_path):
    features = (
        "## F01 — Widget App\n**Priority**: High\n**Status**: not started\n"
        "**Description**: A widget app.\n"
    )
    (tmp_path / ".j2" / "features").mkdir(parents=True)
    (tmp_path / ".j2" / "features" / "features.md").write_text(features)
    tasks_done_dir = tmp_path / ".j2" / "tasks" / "done"
    tasks_done_dir.mkdir(parents=True)
    (tasks_done_dir / "F01.md").write_text("# Tasks for F01\n")

    result = runner.missing_tasks_summary(tmp_path, SETTINGS_FOR_F23)
    assert result == "none"


# --- prev_spec_gaps ---

def test_prev_spec_gaps_reads_from_state_md(tmp_path):
    (tmp_path / ".j2").mkdir(parents=True)
    (tmp_path / ".j2" / "state.md").write_text(
        "completed: refreshed spec\nstate: 3 spec gaps | 2 features need tasks | 5 tasks pending\nnext: /refresh\n"
    )
    assert runner.prev_spec_gaps(tmp_path) == "3"

def test_prev_spec_gaps_defaults_to_zero_when_missing(tmp_path):
    (tmp_path / ".j2").mkdir(parents=True)
    assert runner.prev_spec_gaps(tmp_path) == "0"

def test_prev_spec_gaps_defaults_to_zero_when_no_match(tmp_path):
    (tmp_path / ".j2").mkdir(parents=True)
    (tmp_path / ".j2" / "state.md").write_text("completed: something\nnext: /task-next\n")
    assert runner.prev_spec_gaps(tmp_path) == "0"


# --- F16: /checkpoint command ---

def make_checkpoint_project(tmp_path, features_text, state_text):
    config_dir = tmp_path / ".j2" / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "settings.yaml").write_text(yaml.dump(_base_settings()))
    (config_dir / "workflow.yaml").write_text(yaml.dump(
        {"steps": [{"id": "checkpoint", "template": "checkpoint.md"}]}
    ))
    features_dir = tmp_path / ".j2" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "features.md").write_text(features_text)
    (tmp_path / ".j2" / "state.md").write_text(state_text)
    (tmp_path / ".j2" / "rules.md").write_text("## Rules\n- Write tests.\n")
    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "checkpoint.md").write_text((TEMPLATES_ROOT / "checkpoint.md").read_text())
    return tmp_path


def test_checkpoint_renders_features_and_state(tmp_path):
    state = "completed: finished F01\nstate: 0 spec gaps | 0 features need tasks | 3 tasks pending\nnext: /task-next\n"
    root = make_checkpoint_project(tmp_path, FEATURES_TEXT, state)

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "checkpoint")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = task = request = None

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Directory Scaffold" in output
    assert "finished F01" in output
    assert "{{features}}" not in output
    assert "{{state}}" not in output

def test_checkpoint_template_instructs_write_to_disk(tmp_path):
    content = (TEMPLATES_ROOT / "checkpoint.md").read_text()
    assert "current.md" in content
    assert "write" in content.lower() or "overwrite" in content.lower()

def test_state_loader_reads_state_md(tmp_path):
    (tmp_path / ".j2").mkdir(parents=True)
    state_text = "completed: did something\nstate: 1 spec gaps | 0 features need tasks | 5 tasks pending\nnext: /refresh\n"
    (tmp_path / ".j2" / "state.md").write_text(state_text)

    settings = {"j2": {
        "specs_dir": ".j2/specs",
        "features_file": ".j2/features/features.md",
        "tasks_dir": ".j2/tasks",
        "templates_dir": ".j2/templates",
        "rules_file": ".j2/rules.md",
    }}

    class Args:
        feature = task = request = None

    context = runner.build_context(tmp_path, settings, {"state"}, Args())
    assert "did something" in context["state"]
    assert "/refresh" in context["state"]
