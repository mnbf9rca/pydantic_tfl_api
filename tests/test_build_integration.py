"""Integration tests for the complete build process.

These tests actually run the build_models.py script to catch runtime errors
and validate that the build process works end-to-end.
"""

import os
import shutil
import tempfile
import subprocess
import pytest
from pathlib import Path
from typing import Any

class TestBuildIntegration:
    """Test the complete build process from OpenAPI specs to generated models."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for build output."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def project_root(self):
        """Get the project root directory."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def specs_dir(self, project_root):
        """Get the TfL OpenAPI specs directory."""
        specs_path = project_root / "TfL_OpenAPI_specs"
        if not specs_path.exists():
            pytest.skip("TfL_OpenAPI_specs directory not found")
        return specs_path

    def test_build_process_completes_successfully(self, project_root, specs_dir, temp_output_dir):
        """Test that the build process completes without errors."""
        build_script = project_root / "scripts" / "build_models.py"

        # Run the build process
        result = subprocess.run([
            "uv", "run", "python", str(build_script),
            str(specs_dir),
            temp_output_dir
        ], capture_output=True, text=True, cwd=project_root)

        # Check that the process completed successfully
        assert result.returncode == 0, f"Build failed with error: {result.stderr}"

        # Check that no critical errors were logged
        assert "ERROR" not in result.stderr or "Unexpected error" not in result.stderr

        # Verify success message
        assert "Model generation completed successfully" in result.stderr

    def test_generated_directory_structure(self, project_root, specs_dir, temp_output_dir):
        """Test that the correct directory structure is generated."""
        build_script = project_root / "scripts" / "build_models.py"

        # Run the build process
        result = subprocess.run([
            "uv", "run", "python", str(build_script),
            str(specs_dir),
            temp_output_dir
        ], capture_output=True, text=True, cwd=project_root)

        assert result.returncode == 0, f"Build failed: {result.stderr}"

        output_path = Path(temp_output_dir)

        # Check main directories exist
        assert (output_path / "models").exists(), "models directory not created"
        assert (output_path / "endpoints").exists(), "endpoints directory not created"
        assert (output_path / "core").exists(), "core directory not created"

        # Check core files exist
        core_files = ["__init__.py", "package_models.py"]
        for file_name in core_files:
            file_path = output_path / "core" / file_name
            assert file_path.exists(), f"Core file {file_name} not created"

    def test_models_directory_populated(self, project_root, specs_dir, temp_output_dir):
        """Test that model files are generated in the models directory."""
        build_script = project_root / "scripts" / "build_models.py"

        result = subprocess.run([
            "uv", "run", "python", str(build_script),
            str(specs_dir),
            temp_output_dir
        ], capture_output=True, text=True, cwd=project_root)

        assert result.returncode == 0, f"Build failed: {result.stderr}"

        models_dir = Path(temp_output_dir) / "models"
        model_files = list(models_dir.glob("*.py"))

        # Should have generated multiple model files
        assert len(model_files) > 10, f"Expected multiple model files, got {len(model_files)}"

        # Check that __init__.py exists
        assert (models_dir / "__init__.py").exists(), "models/__init__.py not created"

        # Verify some expected model files exist (common TfL models)
        expected_models = ["Line.py", "StopPoint.py", "Place.py", "Mode.py"]
        for model_file in expected_models:
            model_path = models_dir / model_file
            assert model_path.exists(), f"Expected model file {model_file} not found"

    def test_endpoint_clients_generated(self, project_root, specs_dir, temp_output_dir):
        """Test that endpoint client files are generated."""
        build_script = project_root / "scripts" / "build_models.py"

        result = subprocess.run([
            "uv", "run", "python", str(build_script),
            str(specs_dir),
            temp_output_dir
        ], capture_output=True, text=True, cwd=project_root)

        assert result.returncode == 0, f"Build failed: {result.stderr}"

        endpoints_dir = Path(temp_output_dir) / "endpoints"
        client_files = list(endpoints_dir.glob("*Client.py"))
        config_files = list(endpoints_dir.glob("*Client_config.py"))

        # Should have generated multiple client files
        assert len(client_files) > 5, f"Expected multiple client files, got {len(client_files)}"
        assert len(config_files) > 5, f"Expected multiple config files, got {len(config_files)}"

        # Check that __init__.py exists
        assert (endpoints_dir / "__init__.py").exists(), "endpoints/__init__.py not created"

        # Verify some expected client files
        expected_clients = ["LineClient.py", "StopPointClient.py", "PlaceClient.py"]
        for client_file in expected_clients:
            client_path = endpoints_dir / client_file
            assert client_path.exists(), f"Expected client file {client_file} not found"

    def test_generated_files_are_valid_python(self, project_root, specs_dir, temp_output_dir):
        """Test that all generated files are syntactically valid Python."""
        build_script = project_root / "scripts" / "build_models.py"

        result = subprocess.run([
            "uv", "run", "python", str(build_script),
            str(specs_dir),
            temp_output_dir
        ], capture_output=True, text=True, cwd=project_root)

        assert result.returncode == 0, f"Build failed: {result.stderr}"

        output_path = Path(temp_output_dir)
        python_files = list(output_path.rglob("*.py"))

        assert len(python_files) > 20, f"Expected many Python files, got {len(python_files)}"

        # Test syntax validity by compiling each file
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, str(py_file), 'exec')
            except SyntaxError as e:
                pytest.fail(f"Generated file {py_file} has syntax error: {e}")
            except Exception as e:
                pytest.fail(f"Error reading/compiling {py_file}: {e}")

    def test_build_handles_missing_specs_gracefully(self, project_root, temp_output_dir):
        """Test that build fails gracefully when specs directory is missing."""
        build_script = project_root / "scripts" / "build_models.py"
        nonexistent_specs = "/nonexistent/specs/directory"

        result = subprocess.run([
            "uv", "run", "python", str(build_script),
            nonexistent_specs,
            temp_output_dir
        ], capture_output=True, text=True, cwd=project_root)

        # Should fail but not crash
        assert result.returncode != 0, "Build should fail with missing specs directory"
        assert "ERROR" in result.stderr or "FileNotFoundError" in result.stderr

    def test_build_output_includes_expected_components(self, project_root, specs_dir, temp_output_dir):
        """Test that build output includes all expected components."""
        build_script = project_root / "scripts" / "build_models.py"

        result = subprocess.run([
            "uv", "run", "python", str(build_script),
            str(specs_dir),
            temp_output_dir
        ], capture_output=True, text=True, cwd=project_root)

        assert result.returncode == 0, f"Build failed: {result.stderr}"

        # Check that log indicates expected components were processed
        log_output = result.stderr

        # Should process multiple APIs
        assert "Processing Line" in log_output
        assert "Processing StopPoint" in log_output
        assert "Processing Place" in log_output

        # Should create models
        assert "Created object model:" in log_output
        assert "Created array model:" in log_output

        # Should handle dependencies
        assert "Handling dependencies" in log_output

        # Should save files
        assert "Saving models to files" in log_output
        assert "Creating config and class files" in log_output

    def test_no_critical_runtime_errors(self, project_root, specs_dir, temp_output_dir):
        """Test that no critical runtime errors occur during build."""
        build_script = project_root / "scripts" / "build_models.py"

        result = subprocess.run([
            "uv", "run", "python", str(build_script),
            str(specs_dir),
            temp_output_dir
        ], capture_output=True, text=True, cwd=project_root)

        # Check for specific errors that were previously encountered
        error_patterns = [
            "TypeError: type 'types.UnionType' is not subscriptable",
            "NameError: name 'Set' is not defined",
            "NameError: name 'Dict' is not defined",
            "NameError: name 'List' is not defined",
            "AttributeError:",
            "ImportError:",
        ]

        for pattern in error_patterns:
            assert pattern not in result.stderr, f"Critical error found: {pattern}"

        # Should complete successfully
        assert result.returncode == 0, f"Build failed: {result.stderr}"

    @pytest.mark.slow
    def test_generated_package_can_be_imported(self, project_root, specs_dir, temp_output_dir):
        """Test that the generated package can be imported without errors."""
        build_script = project_root / "scripts" / "build_models.py"

        result = subprocess.run([
            "uv", "run", "python", str(build_script),
            str(specs_dir),
            temp_output_dir
        ], capture_output=True, text=True, cwd=project_root)

        assert result.returncode == 0, f"Build failed: {result.stderr}"

        # Test importing the generated package
        import sys
        sys.path.insert(0, temp_output_dir)

        try:
            # Test importing core components
            from core import ResponseModel, ApiError
            from core.package_models import GenericResponseModel

            # Test importing some models
            from models import Line, StopPoint, Place

            # Test importing some clients
            from endpoints import LineClient, StopPointClient

            # If we get here, imports succeeded
            assert True

        except ImportError as e:
            pytest.fail(f"Generated package could not be imported: {e}")
        finally:
            sys.path.remove(temp_output_dir)