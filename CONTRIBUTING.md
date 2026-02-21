# Contributing to j2

Thanks for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/pitosalas/j2.git
cd j2
python3 -m venv .venv
source .venv/bin/activate
pip install pyyaml pytest
```

## Running Tests

```bash
pytest tests/
```

All tests must pass before submitting a pull request.

## Coding Standards

See `.j2/rules.md` for the coding standards used in this project. Key points:

- Python 3.10+
- `pytest` for all tests — no bare `assert` outside test files
- No bare `except` — always catch specific exception types
- f-strings only, no `.format()`
- Files ≤ 500 lines, functions ≤ 50 lines
- Maximum nesting depth of 2

## Submitting Changes

1. Fork the repository and create a branch from `main`
2. Make your changes and add tests where applicable
3. Run `pytest tests/` and confirm all tests pass
4. Open a pull request with a clear description of what changed and why

## Reporting Bugs

Open an issue using the [bug report template](https://github.com/pitosalas/j2/issues/new?template=bug_report.md).

## Requesting Features

Open an issue using the [feature request template](https://github.com/pitosalas/j2/issues/new?template=feature_request.md).
