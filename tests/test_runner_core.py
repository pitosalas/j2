#!/usr/bin/env python3
"""Unit tests for core runner functions: find_placeholders, fill_template, find_step, extract_*, load_*."""
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

from pathlib import Path

import pytest
import runner
import yaml

from conftest import FEATURES_TEXT, TASKS_TEXT, TEMPLATES_ROOT


WORKFLOW = [
    {"id": "refresh", "template": "refresh.md"},
    {"id": "features-gen", "template": "gen_features.md"},
]


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

def test_extract_feature_case_insensitive():
    result = runner.extract_feature(FEATURES_TEXT, "f01")
    assert "Directory Scaffold" in result


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

def test_extract_task_case_insensitive():
    result = runner.extract_task(TASKS_TEXT, "t01")
    assert "Create directories" in result


# --- load_config / load_workflow ---

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

def test_load_spec_empty_dir_returns_warning(tmp_path):
    settings = {"j2": {"specs_dir": ".j2/specs"}}
    (tmp_path / ".j2" / "specs").mkdir(parents=True)
    result = runner.load_spec(tmp_path, settings)
    assert "no spec files found" in result

def test_build_context_substitutes_placeholder_for_missing_file(tmp_path):
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


FEATURES_WITH_DONE = """\
# Feature List

## F01 — Directory Scaffold
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Creates the directory tree.

---

## F02 — YAML Config
**Priority**: High
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Reads YAML settings.

---

## F03 — Another Done
**Priority**: Medium
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Another completed feature.

---
"""


def test_filter_done_features_strips_done():
    result = runner.filter_done_features(FEATURES_WITH_DONE)
    assert "F02 — YAML Config" in result
    assert "F01 — Directory Scaffold" not in result
    assert "F03 — Another Done" not in result


def test_filter_done_features_count_summary():
    result = runner.filter_done_features(FEATURES_WITH_DONE)
    assert "2 completed features omitted" in result


def test_filter_done_features_no_done():
    result = runner.filter_done_features(FEATURES_TEXT)
    assert "F01" in result
    assert "F02" in result
    assert "completed features omitted" not in result


def test_next_task_template_has_no_spec_or_features():
    template = (TEMPLATES_ROOT / "next_task.md").read_text()
    assert "{{spec}}" not in template
    assert "{{features}}" not in template
