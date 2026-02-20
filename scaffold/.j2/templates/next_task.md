You are helping a developer implement the next pending task in their project.

Follow these coding rules exactly:

--- RULES BEGIN ---
{{rules}}
--- RULES END ---

--- SPEC BEGIN ---
{{spec}}
--- SPEC END ---

--- FEATURES BEGIN ---
{{features}}
--- FEATURES END ---

## Instructions

1. **Check for features without task files first.**
   Scan all features that are not `done`. For each, check whether `.j2/tasks/<feature-id>.md` exists.
   If any not-done feature is missing its task file, stop immediately and tell the user:
   > No task file found for <feature-id>. Run `/tasks-gen <feature-id>` before continuing.
   Do not proceed to step 2.

2. **Find the next feature to work on** (only reached if all not-done features have task files):
   - Look for a feature with **Status**: `in progress` first.
   - Otherwise use the first feature with **Status**: `not started`, highest priority first.
   - Skip features marked `done`.

3. **Find the first not-started task** in that feature's task file.
   - If all tasks in the file are `done`, suggest running `/milestone <feature-id>` and stop.
   - If no not-started tasks exist anywhere across all features, output:
     > No pending tasks found. All features may be complete — consider running `/milestone`.
     Then stop.

4. Implement that task. Follow the rules above. Write clean, working code.

5. After implementing, briefly state:
   - Which feature and task you worked on (e.g. F02 / T03)
   - What you built
   - What the developer should do next (run tests, then `/task-next` again, or `/milestone` if the feature is complete)
