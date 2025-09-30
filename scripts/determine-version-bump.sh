#!/bin/bash
set -e

# Determine version bump type based on production dependency changes in pyproject.toml
# Compares dependency versions between main and release branches
# Returns: major, minor, or patch

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Call the Python script - relies on uv environment in CI, local python3 otherwise
python3 "${SCRIPT_DIR}/determine_version_bump.py" origin/release origin/main
