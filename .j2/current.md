## In Progress

Nothing — all 36 features done.

## Just Completed

- **F36**: `/features-update` now auto-generates task files for newly added features and enforces two-section `features.md` ordering
- **F37**: Added existence guards to `start_task.md`, `next_task.md`, `run_all_tasks.md`, `gen_tasks.md`; fixed `checkpoint.md` idempotency (skip commit if nothing staged)
- **F38**: `/adopt` now detects re-runs and switches to surgical update mode (runner.py + templates + config only; user files untouched)
- Workflow Principles section added to spec (`j2.md`)

## Next Steps

- Run `/milestone F38` to formally close it
- Consider `/deploy` to export a clean copy

## Open Questions

- Pre-existing failures in `test_commands.py` and `test_adopt.py` (scaffold `.claude/commands/` deleted) — needs a separate fix or `/code-review` pass

## Feature Status Summary

| Feature | Status |
|---|---|
| All F01–F38 | done |
| Pre-existing scaffold test failures | unresolved (separate issue) |
