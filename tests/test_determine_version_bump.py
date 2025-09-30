"""Tests for determine_version_bump module."""

import subprocess
from unittest.mock import Mock, patch

import pytest

from scripts.determine_version_bump import (
    compare_versions,
    determine_bump_type,
    extract_dependency_version,
)


class TestCompareVersions:
    """Tests for compare_versions function - our business logic for version comparison."""

    @pytest.mark.parametrize(
        ("old_ver", "new_ver", "expected"),
        [
            # Major bumps
            ("1.0.0", "2.0.0", "major"),
            ("1.9.9", "2.0.0", "major"),
            ("1.2", "2.0", "major"),
            ("1.2", "2.1.1", "major"),
            ("1.2.1", "2.1.3", "major"),
            ("1", "2", "major"),
            # Minor bumps
            ("2.0.0", "2.1.0", "minor"),
            ("2.8.0", "2.9.0", "minor"),
            ("1.2", "1.3", "minor"),
            ("1.2.1", "1.3", "minor"),
            ("1", "1.1", "minor"),
            ("1", "1.1.3", "minor"),
            # Patch bumps
            ("2.8.0", "2.8.1", "patch"),
            ("2.8.1", "2.8.2", "patch"),
            ("2.8", "2.8.2", "patch"),
            ("2.8.0rc1", "2.8.0", "patch"),  # Pre-release to release
            # No change or decrease
            ("2.8.2", "2.8.2", None),  # Equal
            ("2.8.2", "2.8.1", None),  # Decrease
            ("2.1.0", "2.0.0", None),  # Decrease
            ("2.1.0", "1.2.0", None),  # Decrease
            ("2.1.0", "1.2", None),  # Decrease
            ("2.1", "1.2.0", None),  # Decrease
        ],
    )
    def test_version_comparison(self, old_ver: str, new_ver: str, expected: str | None) -> None:
        """Test version comparison logic."""
        assert compare_versions(old_ver, new_ver) == expected


class TestExtractDependencyVersion:
    """Tests for extract_dependency_version function."""

    @pytest.mark.parametrize(
        ("content", "dep_name", "expected"),
        [
            # Standard cases
            (
                """
[project]
dependencies = [
    "pydantic>=2.8.2,<3.0",
    "requests>=2.32.3,<3.0",
]
""",
                "pydantic",
                "2.8.2",
            ),
            (
                """
[project]
dependencies = [
    "pydantic==2.8.2",
]
""",
                "pydantic",
                "2.8.2",
            ),
            # Missing dependency
            (
                """
[project]
dependencies = [
    "requests>=2.32.3,<3.0",
]
""",
                "pydantic",
                None,
            ),
            # No dependencies section
            (
                """
[project]
name = "test"
""",
                "pydantic",
                None,
            ),
        ],
    )
    def test_extract_version(self, content: str, dep_name: str, expected: str | None) -> None:
        """Test extracting dependency versions from pyproject.toml."""
        assert extract_dependency_version(content, dep_name) == expected

    def test_extract_invalid_toml(self) -> None:
        """Test that invalid TOML raises TOMLDecodeError."""
        import tomllib

        with pytest.raises(tomllib.TOMLDecodeError):
            extract_dependency_version("invalid toml {{{", "pydantic")


class TestDetermineBumpType:
    """Tests for determine_bump_type function - our business logic."""

    @pytest.mark.parametrize(
        ("old_content", "new_content", "expected", "description"),
        [
            # No changes
            (
                """
[project]
dependencies = [
    "pydantic>=2.8.2,<3.0",
    "requests>=2.32.3,<3.0",
]
""",
                """
[project]
dependencies = [
    "pydantic>=2.8.2,<3.0",
    "requests>=2.32.3,<3.0",
]
""",
                "patch",
                "No changes returns patch (default)",
            ),
            # Major dependency bump
            (
                """
[project]
dependencies = [
    "pydantic>=2.8.2,<3.0",
    "requests>=2.32.3,<3.0",
]
""",
                """
[project]
dependencies = [
    "pydantic>=3.0.0,<4.0",
    "requests>=2.32.3,<3.0",
]
""",
                "major",
                "Major dependency bump returns major",
            ),
            # Minor dependency bump
            (
                """
[project]
dependencies = [
    "pydantic>=2.8.2,<3.0",
    "requests>=2.32.3,<3.0",
]
""",
                """
[project]
dependencies = [
    "pydantic>=2.9.0,<3.0",
    "requests>=2.32.3,<3.0",
]
""",
                "minor",
                "Minor dependency bump returns minor",
            ),
            # Patch dependency bump
            (
                """
[project]
dependencies = [
    "pydantic>=2.8.2,<3.0",
    "requests>=2.32.3,<3.0",
]
""",
                """
[project]
dependencies = [
    "pydantic>=2.8.3,<3.0",
    "requests>=2.32.3,<3.0",
]
""",
                "patch",
                "Patch dependency bump returns patch",
            ),
            # New dependency
            (
                """
[project]
dependencies = [
    "requests>=2.32.3,<3.0",
]
""",
                """
[project]
dependencies = [
    "pydantic>=2.8.2,<3.0",
    "requests>=2.32.3,<3.0",
]
""",
                "minor",
                "New dependency returns minor",
            ),
            # Removed dependency
            (
                """
[project]
dependencies = [
    "pydantic>=2.8.2,<3.0",
    "requests>=2.32.3,<3.0",
]
""",
                """
[project]
dependencies = [
    "requests>=2.32.3,<3.0",
]
""",
                "major",
                "Removed dependency returns major",
            ),
            # Multiple changes - major takes priority
            (
                """
[project]
dependencies = [
    "pydantic>=2.8.2,<3.0",
    "requests>=2.32.3,<3.0",
]
""",
                """
[project]
dependencies = [
    "pydantic>=3.0.0,<4.0",
    "requests>=2.32.4,<3.0",
]
""",
                "major",
                "Major changes take priority over minor/patch",
            ),
        ],
    )
    @patch("scripts.determine_version_bump.get_pyproject_content")
    def test_dependency_changes(
        self,
        mock_get_content: Mock,
        old_content: str,
        new_content: str,
        expected: str,
        description: str,
    ) -> None:
        """Test version bump determination for various dependency changes."""
        mock_get_content.side_effect = [old_content, new_content]
        assert determine_bump_type("origin/release", "origin/main") == expected

    @patch("scripts.determine_version_bump.get_pyproject_content")
    def test_git_error_returns_patch(self, mock_get_content: Mock) -> None:
        """Test that git errors return safe default (patch)."""
        mock_get_content.side_effect = subprocess.CalledProcessError(1, "git show")
        assert determine_bump_type("origin/release", "origin/main") == "patch"

    @patch("scripts.determine_version_bump.get_pyproject_content")
    def test_toml_parse_error_returns_patch(self, mock_get_content: Mock) -> None:
        """Test that TOML parse errors return safe default (patch)."""
        mock_get_content.return_value = "invalid toml {{{"
        assert determine_bump_type("origin/release", "origin/main") == "patch"
