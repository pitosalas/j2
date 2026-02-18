#!/usr/bin/env bash
# Jacques2 installer
# Copies the scaffold into the current directory and validates the setup.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-.}"

echo "Jacques2 installer"
echo "=================="

# --- Python version check ---
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found. Install Python 3.10 or later." >&2
  exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED="3.10"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"; then
  echo "ERROR: Python $REQUIRED+ required, found $PYTHON_VERSION." >&2
  exit 1
fi
echo "Python $PYTHON_VERSION ... OK"

# --- PyYAML check ---
if ! python3 -c "import yaml" 2>/dev/null; then
  echo "Installing PyYAML..."
  pip3 install --quiet pyyaml
fi
echo "PyYAML ... OK"

# --- Copy scaffold ---
echo "Copying scaffold to $TARGET_DIR ..."
cp -rn "$SCRIPT_DIR/scaffold/." "$TARGET_DIR/"
echo "Scaffold copied."

# --- Validate YAML configs ---
echo "Validating config files..."
for f in "$TARGET_DIR/.planner/config/"*.yaml; do
  python3 -c "import yaml, sys; yaml.safe_load(open('$f'))" \
    && echo "  $f ... OK" \
    || { echo "  ERROR: $f is invalid YAML" >&2; exit 1; }
done

echo ""
echo "Installation complete."
echo "Next steps:"
echo "  1. Edit .planner/config/settings.yaml with your project name."
echo "  2. Add your project spec to .planner/specs/"
echo "  3. Run /spec-review in Claude Code to begin."
