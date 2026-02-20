You are helping a developer take a snapshot of their project for experimentation.

Run this command verbatim to copy all project files into a timestamped snapshot directory:

```bash
rsync -a --ignore-existing --exclude='snapshots/' --exclude='__pycache__' --exclude='*.pyc' . snapshots/$(date +%Y-%m-%dT%H%M)/
```

Then write a brief snapshot summary:
- Timestamp and snapshot directory path
- What is currently in progress (based on feature statuses below, or "project not yet initialized" if features have not been generated)
- Any obvious rough edges or incomplete areas the developer should be aware of while testing

This is not a quality gate. The snapshot is taken as-is.

--- FEATURES BEGIN ---
{{features}}
--- FEATURES END ---
