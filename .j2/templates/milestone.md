You are helping a developer close out a completed feature.

A milestone means the feature is done: implemented, tested, passing, and cleaned up.

The project coding rules define what "done" means. Check each one applies:

--- RULES BEGIN ---
{{rules}}
--- RULES END ---

Review the feature status and write a milestone summary including:
1. **Feature completed** — which feature this milestone covers and what was built.
2. **Rules compliance** — confirm the implementation satisfies every rule (e.g. tests written and passing, packaging conventions followed). List any that are not met.
3. **Quality checklist** — note any cleanup, refactoring, or loose ends addressed.
4. **Updated feature status** — output the complete updated feature entry in a fenced code block using this exact format, so the developer can paste it directly into `features.md`:

```
## FXX — Feature Name
**Priority**: <priority>
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: <existing description unchanged>
```
5. **What's next** — the next feature or task to begin.

If any rule is not satisfied, do NOT declare a milestone — list what must be done first.

When all checks pass and the milestone is granted:

**1. Archive the task file:**

```bash
mv .j2/tasks/<feature-id>.md .j2/tasks/done/<feature-id>.md
```

Replace `<feature-id>` with the actual feature ID (e.g. `F01`).

**2. Reorder the feature entry in `features.md`:**

Open `.j2/features/features.md`. The file has two sections separated by HTML comments: incomplete features (top) and completed features (bottom). Each section is sorted High → Medium → Low priority.

- Remove the feature's full entry block (from its `## FXX —` heading line through and including the closing `---` separator) from the incomplete section.
- Insert it into the completed section in the correct priority position: after the last existing entry of the same or higher priority, before the first entry of lower priority.
- If the completed section is empty, insert it after the `<!-- ===== COMPLETED FEATURES ... -->` comment line.

Before writing the summary, check the task list below. If any task is `not started` or `in progress`, do NOT declare a milestone — list the incomplete tasks and stop.

--- FEATURE BEGIN ---
{{feature}}
--- FEATURE END ---

--- TASKS BEGIN ---
{{tasks}}
--- TASKS END ---
