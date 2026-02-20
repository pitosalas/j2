#!/usr/bin/env python3
"""j2 runner — fills a workflow template with context from disk and prints to stdout."""

import argparse
import re
import sys
from pathlib import Path

import yaml

FOOTER = """
---
End your response with exactly these three lines, formatted with markdown bold labels to make them visually distinct (nothing after them):
**completed:** <one sentence: what was just done>
**state:** <N> spec gaps | <N> features need tasks | <N> tasks pending   ← replace each <N> with an actual integer count
**next:** <the exact slash command to run next, e.g. /task-next or /tasks-gen F11>

Also write these three lines to .j2/state.md (overwriting it), without the markdown bold.
"""


def load_config(root):
    # Read settings.yaml from the project's .j2/config directory.
    path = root / ".j2" / "config" / "settings.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def load_workflow(root):
    # Read workflow.yaml and return the list of step definitions.
    path = root / ".j2" / "config" / "workflow.yaml"
    with open(path) as f:
        return yaml.safe_load(f)["steps"]


def find_step(workflow, command_id):
    # Return the step dict matching command_id, or raise ValueError if not found.
    for step in workflow:
        if step["id"] == command_id:
            return step
    raise ValueError(
        f"Unknown command: {command_id!r}. "
        f"Valid commands: {[s['id'] for s in workflow]}"
    )


def load_template(root, settings, template_name):
    # Read and return the raw text of a prompt template file.
    path = root / settings["j2"]["templates_dir"] / template_name
    return path.read_text()


def find_placeholders(template):
    # Return the set of placeholder names found in {{name}} tokens.
    return set(re.findall(r"\{\{(\w+)\}\}", template))


def load_spec(root, settings):
    # Concatenate all .md files in the specs directory, separated by horizontal rules.
    specs_dir = root / settings["j2"]["specs_dir"]
    parts = [f.read_text() for f in sorted(specs_dir.glob("*.md"))]
    return "\n\n---\n\n".join(parts)


def load_features(root, settings):
    # Read and return the full features file.
    path = root / settings["j2"]["features_file"]
    return path.read_text()


def load_rules(root, settings):
    # Read and return the principles file.
    path = root / settings["j2"]["rules_file"]
    return path.read_text()


def load_tasks(root, settings, feature_id):
    # Read and return the task file for a given feature ID.
    path = root / settings["j2"]["tasks_dir"] / f"{feature_id}.md"
    return path.read_text()


def extract_feature(features_text, feature_id):
    # Extract the markdown section for a single feature (e.g. ## F01 —) from the features file.
    pattern = rf"(^## {re.escape(feature_id.upper())}\b.*?)(?=^## |\Z)"
    match = re.search(pattern, features_text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError(f"Feature {feature_id.upper()!r} not found in features file.")
    return match.group(1).strip()


def extract_task(tasks_text, task_id):
    # Extract the markdown section for a single task (e.g. ### T01 —) from a task file.
    pattern = rf"(^### {re.escape(task_id.upper())}\b.*?)(?=^### |\Z)"
    match = re.search(pattern, tasks_text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError(f"Task {task_id.upper()!r} not found in tasks file.")
    return match.group(1).strip()


def fill_template(template, context):
    # Replace all {{key}} tokens in a single pass so substituted values are not re-scanned.
    def replacer(match):
        return context.get(match.group(1), match.group(0))
    return re.sub(r"\{\{(\w+)\}\}", replacer, template)


def build_context(root, settings, placeholders, args):
    # Load each context value needed by the template, based on which placeholders are present.
    loaders = {
        "spec":       lambda: load_spec(root, settings),
        "rules":      lambda: load_rules(root, settings),
        "features":   lambda: load_features(root, settings),
        "feature":    lambda: extract_feature(load_features(root, settings), args.feature),
        "tasks":      lambda: load_tasks(root, settings, args.feature),
        "task":       lambda: extract_task(load_tasks(root, settings, args.feature), args.task),
        "request":    lambda: args.request,
    }
    context = {}
    for placeholder in placeholders:
        if placeholder not in loaders:
            print(f"Warning: no loader for placeholder {{{{{placeholder}}}}}", file=sys.stderr)
            continue
        try:
            context[placeholder] = loaders[placeholder]()
        except FileNotFoundError as e:
            context[placeholder] = f"(not yet available: {e.filename})"
    return context


def resolve_next_command(root, args):
    # Read state.md and rewrite args.command (and args.feature) from the `next:` line.
    state_path = root / ".j2" / "state.md"
    text = state_path.read_text()
    match = re.search(r"^next:\s+/(\S+)(?:\s+(\S+))?", text, re.MULTILINE)
    if not match:
        raise ValueError("No 'next:' line found in .j2/state.md")
    args.command = match.group(1)
    if match.group(2):
        args.feature = match.group(2)


def main():
    parser = argparse.ArgumentParser(description="j2 template runner")
    parser.add_argument("command", help="Workflow command ID (e.g. task-next), or 'next' to read from state.md")
    parser.add_argument("--feature", default=None, help="Feature ID (e.g. F01)")
    parser.add_argument("--task", default=None, help="Task ID (e.g. T01)")
    parser.add_argument("--request", default=None, help="Refinement request text")
    parser.add_argument("--root", default=".", help="Project root directory (default: cwd)")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    try:
        if args.command == "next":
            resolve_next_command(root, args)
        settings = load_config(root)
        workflow = load_workflow(root)
        step = find_step(workflow, args.command)
        template = load_template(root, settings, step["template"])
        placeholders = find_placeholders(template)
        context = build_context(root, settings, placeholders, args)
        print(fill_template(template, context) + FOOTER)
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
