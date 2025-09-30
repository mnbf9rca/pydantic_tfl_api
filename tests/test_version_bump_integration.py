"""Integration tests for version bump scripts.

These tests verify that the bash wrapper and Python script work correctly together
in a real environment with actual git operations.
"""

import subprocess
from pathlib import Path


class TestBashWrapperIntegration:
    """Integration tests for the bash wrapper script."""

    def test_bash_wrapper_executes_successfully(self) -> None:
        """Test that the bash wrapper can execute the Python script."""
        script_path = Path("scripts/determine-version-bump.sh")
        assert script_path.exists(), "Bash wrapper script not found"

        # The script requires git refs, so this will work if we're in a git repo
        # with the origin/main and origin/release branches
        result = subprocess.run(
            ["bash", str(script_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should output one of: major, minor, patch
        output = result.stdout.strip()
        assert output in ["major", "minor", "patch"], f"Unexpected output: {output}"

        # Should exit successfully
        assert result.returncode == 0, f"Script failed with stderr: {result.stderr}"

    def test_python_script_cli(self) -> None:
        """Test that the Python script CLI works correctly."""
        script_path = Path("scripts/determine_version_bump.py")
        assert script_path.exists(), "Python script not found"

        # Test with actual git refs
        result = subprocess.run(
            ["python3", str(script_path), "origin/release", "origin/main"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should output one of: major, minor, patch
        output = result.stdout.strip()
        assert output in ["major", "minor", "patch"], f"Unexpected output: {output}"

        # Should exit successfully
        assert result.returncode == 0, f"Script failed with stderr: {result.stderr}"

    def test_python_script_cli_usage(self) -> None:
        """Test that the Python script shows usage when called incorrectly."""
        script_path = Path("scripts/determine_version_bump.py")

        # Test with no arguments
        result = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should fail with exit code 1
        assert result.returncode == 1

        # Should print usage message
        assert "Usage:" in result.stderr


class TestUpdateVersionScript:
    """Integration tests for the update_pyproject_version.py script."""

    def test_update_version_script_cli(self, tmp_path: Path) -> None:
        """Test that the update version script works correctly."""
        script_path = Path("scripts/update_pyproject_version.py").resolve()
        assert script_path.exists(), "Update version script not found"

        # Create a temporary pyproject.toml
        test_pyproject = tmp_path / "pyproject.toml"
        test_pyproject.write_text("""[project]
name = "test-package"
version = "1.0.0"
description = "Test package"
""")

        # Run the script with absolute path
        result = subprocess.run(
            ["python3", str(script_path), "2.0.0"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=tmp_path,
        )

        # Should exit successfully
        assert result.returncode == 0, f"Script failed with stderr: {result.stderr}"

        # Check that version was updated
        updated_content = test_pyproject.read_text()
        assert 'version = "2.0.0"' in updated_content
        assert 'version = "1.0.0"' not in updated_content

    def test_update_version_script_usage(self) -> None:
        """Test that the update version script shows usage when called incorrectly."""
        script_path = Path("scripts/update_pyproject_version.py")

        # Test with no arguments
        result = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should fail with exit code 1
        assert result.returncode == 1

        # Should print usage message
        assert "Usage:" in result.stderr
