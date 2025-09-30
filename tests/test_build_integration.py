"""Integration tests for the build process.

These tests verify that the build_models.py script:
1. Completes successfully
2. Creates the expected directory structure
3. Generates valid Python code
4. Produces meaningful content (not empty classes)
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pytest


class TestBuildIntegration:
    """Test the complete build process from OpenAPI specs to generated models."""

    @pytest.fixture(scope="class")
    def build_output(self, project_root: Any, specs_dir: Any) -> Any:
        """Run the build once and share output across all tests in this class."""
        temp_dir = tempfile.mkdtemp()
        build_script = project_root / "scripts" / "build_with_coordinator.py"

        # Run the build process once
        result = subprocess.run(
            ["uv", "run", "python", str(build_script), str(specs_dir), temp_dir],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        # Create a simple object to hold both result and path
        class BuildOutput:
            def __init__(self, result: Any, path: Any) -> None:
                self.result = result
                self.path = path

        yield BuildOutput(result, Path(temp_dir))

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture(scope="class")
    def project_root(self) -> Any:
        """Get the project root directory."""
        return Path(__file__).parent.parent

    @pytest.fixture(scope="class")
    def specs_dir(self, project_root: Any) -> Any:
        """Get the TfL OpenAPI specs directory."""
        specs_path = project_root / "TfL_OpenAPI_specs"
        if not specs_path.exists():
            pytest.skip("TfL_OpenAPI_specs directory not found")
        return specs_path

    def test_build_completes_successfully(self, build_output: Any) -> None:
        """Test that the build process completes without errors."""
        assert build_output.result.returncode == 0, f"Build failed: {build_output.result.stderr}"

        # Check for critical errors in output
        stderr = build_output.result.stderr
        assert "ERROR" not in stderr or "Unexpected error" not in stderr
        assert "Build completed successfully" in stderr

    def test_creates_expected_directories(self, build_output: Any) -> None:
        """Test that required directories are created and populated."""
        required_dirs = {
            "models": "Model definitions",
            "endpoints": "API client endpoints",
            "core": "Core infrastructure files",
        }

        for dir_name, description in required_dirs.items():
            dir_path = build_output.path / dir_name
            assert dir_path.exists(), f"Missing {description} directory: {dir_name}"

            # Verify directory has content
            py_files = list(dir_path.glob("*.py"))
            assert py_files, f"{dir_name} directory is empty"

            # Check __init__.py exists
            init_file = dir_path / "__init__.py"
            assert init_file.exists(), f"Missing __init__.py in {dir_name}"

    @pytest.mark.parametrize(
        "model_type,sample_file,content_markers",
        [
            # Test a complex BaseModel
            (
                "BaseModel",
                "models/Line.py",
                [
                    "class Line(BaseModel)",
                    "id: str | None = Field(None)",  # Has ID field with modern syntax
                    "name: str | None = Field(None)",  # Has name field with modern syntax
                    "model_config = ConfigDict",  # Has Pydantic config
                ],
            ),
            # Test an Enum has values
            (
                "Enum",
                "models/CategoryEnum.py",
                [
                    "class CategoryEnum(Enum)",
                    "REALTIME =",  # Has enum value
                    "INFORMATION =",  # Has another value
                ],
            ),
            # Test a RootModel array
            (
                "RootModel",
                "models/LineArray.py",
                [
                    "class LineArray(RootModel",
                    "list[Line]",  # References actual model type
                    "from .Line import Line",  # Imports the model
                ],
            ),
            # Test an endpoint client
            (
                "Client",
                "endpoints/LineClient.py",
                [
                    "class LineClient",
                    "_send_request_and_deserialize",  # Uses base client method
                    "def Line",  # Has at least one API method
                    "-> ResponseModel",  # Returns proper response types
                ],
            ),
        ],
    )
    def test_sample_models_have_meaningful_content(
        self, build_output: Any, model_type: Any, sample_file: Any, content_markers: Any
    ) -> None:
        """Test that different model types contain actual content, not empty shells."""
        file_path = build_output.path / sample_file

        # File should exist
        assert file_path.exists(), f"Expected {model_type} file not found: {sample_file}"

        content = file_path.read_text()

        # Check all expected content markers
        for marker in content_markers:
            assert marker in content, f"{model_type} missing expected content: {marker}"

        # Verify it's not trivially small (different thresholds for different types)
        min_size = 100 if model_type == "RootModel" else 200  # Arrays are smaller
        assert len(content) > min_size, f"{model_type} file seems too small to be meaningful"

    def test_all_generated_python_is_syntactically_valid(self, build_output: Any) -> None:
        """Test that ALL generated Python files compile without syntax errors."""
        import compileall
        import sys
        from io import StringIO

        # Capture compileall output
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        captured_output = StringIO()

        try:
            sys.stdout = captured_output
            sys.stderr = captured_output

            # Compile all Python files recursively
            success = compileall.compile_dir(
                str(build_output.path),
                quiet=1,  # Suppress normal output
                force=True,  # Compile even if .pyc exists
                legacy=False,  # Use __pycache__ directory
            )

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        output = captured_output.getvalue()

        # Check that compilation succeeded
        assert success, f"Some Python files failed to compile:\n{output}"

        # Check for syntax errors in the output
        assert "SyntaxError" not in output, f"Syntax errors found in generated code:\n{output}"

    def test_model_imports_resolve_correctly(self, build_output: Any) -> None:
        """Test that models can import their dependencies."""
        # Check a few files that we expect to have imports
        files_with_imports = [
            build_output.path / "models" / "LineArray.py",  # Imports Line
            build_output.path / "models" / "Place.py",  # Self-referential
            build_output.path / "models" / "Journey.py",  # Complex dependencies
        ]

        models_dir = build_output.path / "models"

        for file_path in files_with_imports:
            # These files MUST exist - the build should have created them
            assert file_path.exists(), f"Expected model file not found: {file_path.name}"

            content = file_path.read_text()

            # Find relative imports: from .SomeModel import SomeModel
            import_pattern = r"from \.([\w]+) import"
            imports = re.findall(import_pattern, content)

            for module_name in imports:
                imported_file = models_dir / f"{module_name}.py"
                assert imported_file.exists(), f"{file_path.name} imports non-existent {module_name}"

    def test_build_fails_gracefully_with_invalid_input(self, project_root: Any) -> None:
        """Test that build handles missing specs directory gracefully."""
        build_script = project_root / "scripts" / "build_with_coordinator.py"
        temp_dir = tempfile.mkdtemp()

        try:
            result = subprocess.run(
                ["uv", "run", "python", str(build_script), "/nonexistent/path", temp_dir],
                capture_output=True,
                text=True,
                cwd=project_root,
            )

            # Should fail with non-zero exit code
            assert result.returncode != 0, "Build should fail with invalid input"

            # Should have meaningful error message
            assert "ERROR" in result.stderr or "FileNotFoundError" in result.stderr

        finally:
            shutil.rmtree(temp_dir)

    def test_build_logs_show_progress(self, build_output: Any) -> None:
        """Test that build provides informative progress messages."""
        logs = build_output.result.stderr

        # Should show processing of major components
        progress_indicators = [
            "Processing",  # Shows it's working on files
            "Created",  # Shows models being created
            "Handling dependencies",  # Shows dependency resolution
            "Saving models",  # Shows file writing
        ]

        for indicator in progress_indicators:
            assert indicator in logs, f"Build logs missing progress indicator: {indicator}"
