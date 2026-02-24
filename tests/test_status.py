#!/usr/bin/env python3
# test_status.py — tests for /status command (F40)
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

from pathlib import Path
import yaml

TEMPLATES_DIR = Path(__file__).parent.parent / ".j2" / "templates"
CONFIG_DIR = Path(__file__).parent.parent / ".j2" / "config"
COMMANDS_DIR = Path(__file__).parent.parent / ".claude" / "commands"


def test_status_template_exists():
    assert (TEMPLATES_DIR / "status.md").is_file()


def test_status_template_has_features_placeholder():
    content = (TEMPLATES_DIR / "status.md").read_text()
    assert "{{features}}" in content


def test_status_template_has_state_placeholder():
    content = (TEMPLATES_DIR / "status.md").read_text()
    assert "{{state}}" in content


def test_status_workflow_registered():
    workflow = yaml.safe_load((CONFIG_DIR / "workflow.yaml").read_text())
    ids = {s["id"]: s for s in workflow["steps"]}
    assert "status" in ids
    assert ids["status"]["template"] == "status.md"


def test_status_command_exists():
    assert (COMMANDS_DIR / "status.md").is_file()


def test_status_command_calls_runner():
    content = (COMMANDS_DIR / "status.md").read_text()
    assert "runner.py status" in content
