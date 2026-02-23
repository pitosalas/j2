## In Progress
Nothing actively in progress.

## Just Completed
Refactored the "auto-mark feature done when last task completes" approach:
- Reverted changes to `run_all_tasks.md`, `start_task.md`, `next_task.md` that would have broken parallel safety
- Moved the feature-status sync logic to `checkpoint.md` (already exclusive-access, already touches shared files)
- Updated `j2.md`, `features.md` (F16), and `README.md` to document the new `/checkpoint` sync behavior

## What's Next
No pending tasks or features. Options:
- `/features-update` to add new features
- `/deploy` to ship

## Open Questions
None.

## Feature Status Summary

| Feature | Status |
|---|---|
| All 33 features | done |
