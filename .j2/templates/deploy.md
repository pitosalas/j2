Target directory: {{target}}

Run the following commands (the path may be relative or absolute):

```bash
mkdir -p "{{target}}" && bash scaffold/install.sh "{{target}}"
```

If the commands succeed, report:
- The full output from install.sh
- The absolute path of the new project directory
- The next step: `cd <directory>` then open Claude Code and run `/refresh`

If any command fails, report the error output and stop — do not attempt partial recovery.

The directory may already exist — install.sh uses `--ignore-existing` and will not overwrite user files.
