## In Progress

Nothing — all 38 features done.

## Just Completed

- **F39**: `/milestone` project-complete gate (no-arg invocation scans all features, runs pytest, then checkpoints)
- **F40**: `/status` command — template, workflow.yaml entry, slash command, 6 tests
- **`/status` refactor**: moved all computation into `runner.py` (`compute_status()`), bypasses template system, outputs final text directly — eliminates extra tool calls
- Deployed updated `runner.py` + new templates/commands to `brh-website-2` via `/adopt` surgical update

## Next Steps

- Add new features via `/features-update`, or
- Ship with `/deploy`

## Open Questions

- User evaluating whether the single Bash tool call block in `/status` output is acceptable vs. a shell alias approach.

## Feature Status Summary

| Feature | Status |
|---|---|
| All F01–F40 | done |
