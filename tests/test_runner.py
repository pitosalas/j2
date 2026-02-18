"""Tests for scaffold/.planner/runner.py"""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scaffold" / ".planner"))
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
    config_dir = tmp_path / ".planner" / "config"
    config_dir.mkdir(parents=True)
    settings = {"project": {"name": "test"}, "planner": {"specs_dir": ".planner/specs"}}
    (config_dir / "settings.yaml").write_text(yaml.dump(settings))
    result = runner.load_config(tmp_path)
    assert result["project"]["name"] == "test"

def test_load_workflow(tmp_path):
    config_dir = tmp_path / ".planner" / "config"
    config_dir.mkdir(parents=True)
    workflow = {"steps": [{"id": "spec-review", "template": "spec_review.md"}]}
    (config_dir / "workflow.yaml").write_text(yaml.dump(workflow))
    result = runner.load_workflow(tmp_path)
    assert result[0]["id"] == "spec-review"

def test_load_config_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        runner.load_config(tmp_path)


# --- build_context graceful fallback ---

def test_build_context_substitutes_placeholder_for_missing_file(tmp_path):
    # Missing files should produce a descriptive placeholder, not crash.
    settings = {
        "planner": {
            "features_file": ".planner/features/features.md",
            "specs_dir": ".planner/specs",
            "rules_file": ".planner/rules.md",
            "tasks_dir": ".planner/tasks",
            "templates_dir": ".planner/templates",
        }
    }

    class FakeArgs:
        feature = "F01"
        task = "T01"
        request = None

    context = runner.build_context(tmp_path, settings, {"features"}, FakeArgs())
    assert "features" in context
    assert "not yet available" in context["features"]
