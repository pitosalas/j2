You are helping a developer deploy the j2 scaffold to a new project directory.

The target directory is: {{request}}

Run the following commands:

```bash
mkdir -p {{request}} && bash scaffold/install.sh {{request}} && cp .j2/runner.py {{request}}/.j2/runner.py
```

Report the result, including the full output from the install script. If the directory already exists, that is fine — install.sh uses `--ignore-existing` and will not overwrite files. The `cp` step ensures the deployed project gets the current authoritative `runner.py` from `.j2/`.
