#!/usr/bin/env python3
"""Shared constants and sys.path setup for the runner test suite."""
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / ".j2"))

SCAFFOLD_ROOT = Path(__file__).parent.parent / "scaffold"
J2_ROOT = Path(__file__).parent.parent / ".j2"
TEMPLATES_ROOT = J2_ROOT / "templates"
CONFIG_ROOT = J2_ROOT / "config"
SCAFFOLD = SCAFFOLD_ROOT

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

MIXED_PRIORITY_FEATURES = """\
## F01 — Low Feature
**Priority**: Low
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Low priority thing.

---

## F02 — High Feature
**Priority**: High
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: High priority thing.

---

## F03 — Medium Feature
**Priority**: Medium
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: Medium priority thing.

---
"""

MILESTONE_TASKS_TEXT = """\
# Tasks for F01

### T01 — Create directories
**Status**: done
**Description**: Make all required subdirectories.

### T02 — Write tests
**Status**: done
**Description**: Write tests for directory creation.
"""

SETTINGS_FOR_F23 = {
    "j2": {
        "specs_dir": ".j2/specs",
        "features_file": ".j2/features/features.md",
        "tasks_dir": ".j2/tasks",
        "templates_dir": ".j2/templates",
        "rules_file": ".j2/rules.md",
    }
}
