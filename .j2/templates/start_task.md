Output ONLY the following line and nothing else, then stop and wait for the user's input:

`Feature ID [{{default_feature}}]: `

After the user responds with a feature ID, read the task file at `.j2/tasks/<feature-id>.md` directly. Find the first task whose `**Status**` is `not started` and implement it. You must follow the coding principles below exactly.

--- PRINCIPLES BEGIN ---
{{rules}}
--- PRINCIPLES END ---

After writing the code:
1. Update that task's `**Status**` to `done` in the task file.
2. Briefly explain what you implemented and any decisions you made.
3. State what the developer should do next (run tests, then `/task-start` again or `/milestone` if the feature is complete).

--- SPEC BEGIN ---
{{spec}}
--- SPEC END ---

--- FEATURES BEGIN ---
{{features}}
--- FEATURES END ---
