#!/usr/bin/env python3
"""Update version field in pyproject.toml.

This script safely updates the version field in pyproject.toml using TOML parsing
to ensure correct handling regardless of file formatting.
"""

import sys
import tomllib
from pathlib import Path


def update_version(pyproject_path: Path, new_version: str) -> None:
    """Update version in pyproject.toml file.

    Args:
        pyproject_path: Path to pyproject.toml file
        new_version: New version string to set

    Raises:
        FileNotFoundError: If pyproject.toml doesn't exist
        ValueError: If project.version field not found
        tomllib.TOMLDecodeError: If TOML is invalid
    """
    # Read and parse TOML
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    # Validate structure
    if "project" not in data or "version" not in data["project"]:
        raise ValueError("Could not find project.version in pyproject.toml")

    # Read original file content
    with open(pyproject_path, encoding="utf-8") as f:
        lines = f.readlines()

    # Find and replace version line
    old_version = data["project"]["version"]
    version_updated = False

    for i, line in enumerate(lines):
        # Match version = "..." with various formatting
        if line.strip().startswith("version") and "=" in line:
            # Preserve original indentation and formatting
            indent = line[: len(line) - len(line.lstrip())]
            # Update version while preserving quote style
            if f'"{old_version}"' in line:
                lines[i] = f'{indent}version = "{new_version}"\n'
            elif f"'{old_version}'" in line:
                lines[i] = f"{indent}version = '{new_version}'\n"
            else:
                # Fallback: use double quotes
                lines[i] = f'{indent}version = "{new_version}"\n'
            version_updated = True
            break

    if not version_updated:
        raise ValueError(f"Could not find version line with value {old_version}")

    # Write updated content
    with open(pyproject_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"Updated version to {new_version}")


def main() -> None:
    """Main entry point for CLI usage."""
    if len(sys.argv) != 2:
        print("Usage: update_pyproject_version.py <new_version>", file=sys.stderr)
        sys.exit(1)

    new_version = sys.argv[1]
    pyproject_path = Path("pyproject.toml")

    try:
        update_version(pyproject_path, new_version)
    except FileNotFoundError:
        print("Error: pyproject.toml not found", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to update version: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
