#!/usr/bin/env python3
"""Determine semantic version bump based on production dependency changes.

Compares dependency versions between two git refs and determines the appropriate
semantic version bump (major, minor, or patch) based on the most significant change.
"""

import subprocess
import sys
import tomllib
from typing import Literal

from packaging.requirements import Requirement
from packaging.version import Version

BumpType = Literal["major", "minor", "patch"]

# Production dependencies to check
PRODUCTION_DEPENDENCIES = ["pydantic", "requests"]


def get_pyproject_content(git_ref: str) -> str:
    """Get pyproject.toml content from a specific git ref.

    Args:
        git_ref: Git reference (e.g., 'origin/main', 'HEAD')

    Returns:
        Content of pyproject.toml as string

    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    result = subprocess.run(
        ["git", "show", f"{git_ref}:pyproject.toml"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def extract_dependency_version(content: str, dep_name: str) -> str | None:
    """Extract version for a specific dependency from pyproject.toml content.

    Uses packaging.requirements.Requirement for proper PEP 508 parsing.

    Args:
        content: pyproject.toml content as string
        dep_name: Name of the dependency to find

    Returns:
        Version string (e.g., "2.8.2") or None if not found

    Raises:
        tomllib.TOMLDecodeError: If content is not valid TOML
    """
    data = tomllib.loads(content)
    dependencies = data.get("project", {}).get("dependencies", [])

    for dep in dependencies:
        if not isinstance(dep, str):
            continue

        try:
            req = Requirement(dep.strip())
        except Exception:
            # Skip invalid requirement strings
            continue

        # Check if this is the dependency we're looking for
        if req.name.lower() != dep_name.lower():
            continue

        # Extract version from specifier
        # Look for >= or == operators to get the base version
        for spec in req.specifier:
            if spec.operator in (">=", "==", "~="):
                return spec.version

        # If no >= or ==, try to get any version from the specifier
        if req.specifier:
            # Get first specifier's version as fallback
            return next(iter(req.specifier)).version

    return None


def compare_versions(old_ver: str, new_ver: str) -> BumpType | None:
    """Compare two versions and determine bump type using PEP 440 standards.

    Uses packaging.version.Version for robust version comparison that handles:
    - Standard versions: "1.2.3"
    - Two-part versions: "1.2" (normalized to "1.2.0")
    - Pre-releases: "1.2.3rc1", "1.2.3a1"
    - Post-releases: "1.2.3.post1"
    - Calendar versioning: "2025.1.1"

    Args:
        old_ver: Old version string
        new_ver: New version string

    Returns:
        "major", "minor", "patch", or None if versions are equal or decreased

    Raises:
        packaging.version.InvalidVersion: If version format is invalid
    """
    old = Version(old_ver)
    new = Version(new_ver)

    if old >= new:
        return None

    # Access base_version to get the normalized version without pre/post/dev suffixes
    old_release = old.release
    new_release = new.release

    # Ensure we have at least (major, minor, patch)
    old_parts = old_release + (0,) * (3 - len(old_release))
    new_parts = new_release + (0,) * (3 - len(new_release))

    old_major, old_minor, old_patch = old_parts[:3]
    new_major, new_minor, new_patch = new_parts[:3]

    # Compare major versions
    if new_major > old_major:
        return "major"

    # If major versions equal, check minor and patch
    if new_major == old_major:
        # Compare minor versions
        if new_minor > old_minor:
            return "minor"

        # Compare patch versions
        if new_minor == old_minor and new_patch > old_patch:
            return "patch"

    # Version increased in pre/post/dev only - treat as patch
    return "patch"


def _handle_dependency_change(
    dep: str,
    old_version: str | None,
    new_version: str | None,
    old_ref: str,
    new_ref: str,
) -> BumpType | None:
    """Handle a single dependency change and determine its bump type.

    Args:
        dep: Dependency name
        old_version: Version in old ref, or None if not found
        new_version: Version in new ref, or None if not found
        old_ref: Old git reference name (for logging)
        new_ref: New git reference name (for logging)

    Returns:
        Bump type for this change, or None if no change
    """
    print(
        f"[INFO] {dep}: {old_version or 'NOT FOUND'} ({old_ref}) vs {new_version or 'NOT FOUND'} ({new_ref})",
        file=sys.stderr,
    )

    # New dependency added
    if old_version is None and new_version is not None:
        print(f"[WARN] {dep}: New dependency added in {new_ref} ({new_version})", file=sys.stderr)
        return "minor"

    # Dependency removed
    if old_version is not None and new_version is None:
        print(f"[WARN] {dep}: Dependency removed from {new_ref}", file=sys.stderr)
        return "major"

    # Missing in both refs
    if old_version is None:
        print(f"[WARN] {dep}: Dependency not found in either ref", file=sys.stderr)
        return None

    # No version change
    if old_version == new_version:
        return None

    # Compare versions
    assert old_version is not None and new_version is not None
    try:
        if (dep_bump := compare_versions(old_version, new_version)):
            print(
                f"[INFO] {dep}: {dep_bump.capitalize()} version bump detected ({old_version} → {new_version})",
                file=sys.stderr,
            )
            return dep_bump
        print(
            f"[WARN] {dep}: Version changed but not a standard bump ({old_version} → {new_version})",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"[WARN] {dep}: Failed to parse version: {e}", file=sys.stderr)

    return None


def _apply_bump_priority(current: BumpType, new: BumpType | None) -> BumpType:
    """Apply bump type priority rules: major > minor > patch.

    Args:
        current: Current bump type
        new: New bump type to consider

    Returns:
        Highest priority bump type
    """
    if new is None:
        return current
    if new == "major":
        return "major"
    return "minor" if new == "minor" and current != "major" else current


def determine_bump_type(
    old_ref: str,
    new_ref: str,
    dependencies: list[str] | None = None,
) -> BumpType:
    """Determine version bump type based on dependency changes between two git refs.

    Args:
        old_ref: Old git reference (e.g., 'origin/release')
        new_ref: New git reference (e.g., 'origin/main')
        dependencies: List of dependency names to check. Defaults to PRODUCTION_DEPENDENCIES.

    Returns:
        Bump type: "major", "minor", or "patch"

    Priority: major > minor > patch
    - New dependency → minor
    - Removed dependency → major
    - Dependency major bump → major
    - Dependency minor bump → minor
    - Dependency patch bump → patch
    - No changes → patch (default)
    """
    if dependencies is None:
        dependencies = PRODUCTION_DEPENDENCIES

    try:
        old_content = get_pyproject_content(old_ref)
        new_content = get_pyproject_content(new_ref)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to get pyproject.toml from git: {e}", file=sys.stderr)
        return "patch"  # Safe default

    bump_type: BumpType = "patch"

    for dep in dependencies:
        try:
            old_version = extract_dependency_version(old_content, dep)
            new_version = extract_dependency_version(new_content, dep)
        except tomllib.TOMLDecodeError as e:
            print(f"Error: Failed to parse pyproject.toml: {e}", file=sys.stderr)
            return "patch"  # Safe default

        # Handle this dependency change and apply priority rules
        dep_bump = _handle_dependency_change(dep, old_version, new_version, old_ref, new_ref)
        bump_type = _apply_bump_priority(bump_type, dep_bump)

    print(f"[INFO] Determined bump type: {bump_type}", file=sys.stderr)
    return bump_type


def main() -> None:
    """Main entry point for CLI usage."""
    if len(sys.argv) < 3:
        print("Usage: determine_version_bump.py <old_ref> <new_ref>", file=sys.stderr)
        sys.exit(1)

    old_ref = sys.argv[1]
    new_ref = sys.argv[2]

    bump_type = determine_bump_type(old_ref, new_ref)
    print(bump_type)


if __name__ == "__main__":
    main()
