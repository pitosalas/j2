You are helping a developer take a snapshot of their project for experimentation.

Copy all project files into a timestamped directory under `snapshots/` (e.g., `snapshots/2026-02-18T1045/`) so the developer can test the current state as a standalone project without affecting the working directory. Use the current date and time for the timestamp.

Use this command to copy, so that any files already present in the snapshot directory (e.g. user-customized templates from a previous run) are never overwritten:

```bash
rsync -a --ignore-existing --exclude='snapshots/' --exclude='__pycache__' --exclude='*.pyc' . snapshots/TIMESTAMP/
```

Then write a brief snapshot summary:
- Timestamp and snapshot directory path
- What is currently in progress (based on feature statuses below, or "project not yet initialized" if features have not been generated)
- Any obvious rough edges or incomplete areas the developer should be aware of while testing

This is not a quality gate. The snapshot is taken as-is.

--- FEATURES BEGIN ---
{{features}}
--- FEATURES END ---
