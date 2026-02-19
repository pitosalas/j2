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

1. Find the next task to work on:
   - Look for a feature with **Status**: `in progress` first. If found, use it.
   - Otherwise use the first feature with **Status**: `not started` that has High priority.
   - Skip features marked `done`.

2. Read the task file for that feature from `.j2/tasks/<feature-id>.md`.
   If no task file exists yet, tell the user to run `/gen-tasks <feature-id>` first.

3. Find the first task in that file that has not been implemented yet.
   If all tasks appear done, tell the user and suggest running `/milestone`.

4. Implement that task. Follow the rules above. Write clean, working code.

5. After implementing, briefly state:
   - Which feature and task you worked on (e.g. F02 / T03)
   - What you built
   - What the developer should do next (run tests, then `/next-task` again, or `/milestone` if the feature is complete)
