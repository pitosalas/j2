#!/usr/bin/env python3
"""Tests for F34: /adopt command — workflow entry, template rendering, slash command files."""
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

from pathlib import Path

import runner
import yaml

from conftest import CONFIG_ROOT, TEMPLATES_ROOT


# --- T05-1: adopt step exists in workflow.yaml ---

def test_adopt_workflow_entry_exists():
    workflow = yaml.safe_load((CONFIG_ROOT / "workflow.yaml").read_text())
    step_ids = [s["id"] for s in workflow["steps"]]
    assert "adopt" in step_ids
    step = next(s for s in workflow["steps"] if s["id"] == "adopt")
    assert step["template"] == "adopt.md"
    assert step["command"] == "/adopt"


# --- T05-2: adopt template renders without errors ---

def test_adopt_template_contains_rules_placeholder():
    template = (TEMPLATES_ROOT / "adopt.md").read_text()
    assert "{{rules}}" in template


def test_adopt_template_has_no_spec_or_features_placeholder():
    template = (TEMPLATES_ROOT / "adopt.md").read_text()
    assert "{{spec}}" not in template
    assert "{{features}}" not in template


def make_adopt_project(tmp_path, rules_text):
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
        {"steps": [{"id": "adopt", "template": "adopt.md"}]}
    ))
    (tmp_path / ".j2" / "rules.md").write_text(rules_text)
    templates_dir = tmp_path / ".j2" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "adopt.md").write_text((TEMPLATES_ROOT / "adopt.md").read_text())
    return tmp_path


def test_adopt_renders_rules_without_missing_placeholders(tmp_path):
    rules = "## Testing\n- Each feature must have at least one test.\n"
    root = make_adopt_project(tmp_path, rules)

    settings = runner.load_config(root)
    workflow = runner.load_workflow(root)
    step = runner.find_step(workflow, "adopt")
    template = runner.load_template(root, settings, step["template"])
    placeholders = runner.find_placeholders(template)

    class Args:
        feature = task = request = target = None

    context = runner.build_context(root, settings, placeholders, Args())
    output = runner.fill_template(template, context)

    assert "Each feature must have at least one test" in output
    assert "{{rules}}" not in output


# --- T05-3: adopt slash command files exist with correct runner invocation ---

def test_adopt_slash_command_exists_and_calls_runner():
    cmd_path = Path(__file__).parent.parent / ".claude" / "commands" / "adopt.md"
    assert cmd_path.exists()
    content = cmd_path.read_text()
    assert "runner.py adopt" in content


def test_adopt_scaffold_command_exists_and_calls_runner():
    cmd_path = Path(__file__).parent.parent / "scaffold" / ".claude" / "commands" / "adopt.md"
    assert cmd_path.exists()
    content = cmd_path.read_text()
    assert "runner.py adopt" in content


def test_adopt_command_takes_no_arguments():
    cmd_path = Path(__file__).parent.parent / ".claude" / "commands" / "adopt.md"
    content = cmd_path.read_text()
    assert "$ARGUMENTS" not in content


def test_adopt_template_contains_rerun_detection():
    template = (TEMPLATES_ROOT / "adopt.md").read_text()
    assert "already" in template.lower() or "re-run" in template.lower() or "surgical" in template.lower()
    assert "runner.py" in template
    assert "templates" in template
