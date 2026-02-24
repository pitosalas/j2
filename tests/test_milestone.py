#!/usr/bin/env python3
# test_milestone.py — tests for /milestone template (F39: project-complete gate)
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / ".j2" / "templates"
MILESTONE_TEMPLATE = TEMPLATES_DIR / "milestone.md"


def test_milestone_template_contains_no_arg_detection():
    content = MILESTONE_TEMPLATE.read_text()
    assert "feature_arg_provided" in content


def test_milestone_template_contains_incomplete_feature_scan():
    content = MILESTONE_TEMPLATE.read_text()
    assert "NOT `done`" in content or "not `done`" in content or "incomplete" in content.lower()


def test_milestone_template_contains_pytest_call():
    content = MILESTONE_TEMPLATE.read_text()
    assert "pytest" in content


def test_milestone_template_single_feature_mode_present():
    content = MILESTONE_TEMPLATE.read_text()
    assert "feature_arg_provided" in content
    assert "yes" in content
