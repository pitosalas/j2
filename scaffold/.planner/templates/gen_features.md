You are helping a developer plan a software project.

Keep these coding principles in mind when generating features — they will constrain how each feature is implemented:

--- PRINCIPLES BEGIN ---
{{principles}}
--- PRINCIPLES END ---

Read the following project specification and generate a feature list.

For each feature:
- Assign a short ID (F01, F02, ...)
- Give it a concise name
- Write a 1-2 sentence description
- Assign a priority: High, Medium, or Low
- Include status fields initialized to their default values

Format each feature as:

## F01 — Feature Name
**Priority**: High
**Status**: not started | Tests written: no | Tests passing: n/a
**Description**: ...

Order features from most to least important. Focus on concrete, buildable features.
Do not include features that are not clearly supported by the spec.

--- SPEC BEGIN ---
{{spec}}
--- SPEC END ---
