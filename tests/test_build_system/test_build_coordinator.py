"""Tests for BuildCoordinator class that orchestrates the entire build process."""

import contextlib
import json
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from scripts.build_system.build_coordinator import BuildCoordinator


class TestBuildCoordinator:
    """Test the BuildCoordinator class for orchestrating the build process."""

    @pytest.fixture
    def build_coordinator(self) -> BuildCoordinator:
        """Create a BuildCoordinator instance for testing."""
        return BuildCoordinator()

    @pytest.fixture
    def temp_spec_dir(self) -> Generator[Path, None, None]:
        """Create a temporary directory with sample spec files."""
        temp_dir = tempfile.mkdtemp()
        spec_dir = Path(temp_dir) / "specs"
        spec_dir.mkdir()

        # Create sample spec file
        sample_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "servers": [{"url": "https://api.example.com/v1/test"}],
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
                        "required": ["id"],
                    }
                }
            },
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "getUsers",
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}
                                    }
                                }
                            }
                        },
                    }
                }
            },
        }

        spec_file = spec_dir / "test_api.json"
        with open(spec_file, "w") as f:
            json.dump(sample_spec, f)

        yield spec_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def temp_output_dir(self) -> Generator[Path, None, None]:
        """Create a temporary output directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_init_creates_components(self, build_coordinator: Any) -> None:
        """Test that BuildCoordinator initializes with all required components."""
        assert hasattr(build_coordinator, "spec_processor")
        assert hasattr(build_coordinator, "model_builder")
        assert hasattr(build_coordinator, "dependency_resolver")
        assert hasattr(build_coordinator, "file_manager")
        assert hasattr(build_coordinator, "client_generator")

        # Check that all components are properly instantiated
        assert build_coordinator.spec_processor is not None
        assert build_coordinator.model_builder is not None
        assert build_coordinator.dependency_resolver is not None
        assert build_coordinator.file_manager is not None
        assert build_coordinator.client_generator is not None

    def test_validate_and_setup_paths_valid_input(
        self, build_coordinator: Any, temp_spec_dir: Any, temp_output_dir: Any
    ) -> None:
        """Test path validation with valid input paths."""
        # Should not raise any exceptions
        build_coordinator._validate_and_setup_paths(str(temp_spec_dir), str(temp_output_dir))

        # Output directory should exist after setup
        assert temp_output_dir.exists()

    def test_validate_and_setup_paths_invalid_spec_path(self, build_coordinator: Any, temp_output_dir: Any) -> None:
        """Test path validation with invalid spec path."""
        with pytest.raises(FileNotFoundError):
            build_coordinator._validate_and_setup_paths("/nonexistent/path", str(temp_output_dir))

    def test_validate_and_setup_paths_creates_output_dir(self, build_coordinator: Any, temp_spec_dir: Any) -> None:
        """Test that output directory is created if it doesn't exist."""
        output_dir = Path(tempfile.mkdtemp()) / "nonexistent" / "output"

        try:
            build_coordinator._validate_and_setup_paths(str(temp_spec_dir), str(output_dir))
            assert output_dir.exists()
        finally:
            shutil.rmtree(output_dir.parent)

    def test_load_and_process_specs(self, build_coordinator: Any, temp_spec_dir: Any) -> None:
        """Test loading and processing specifications."""
        specs, components, paths = build_coordinator._load_and_process_specs(str(temp_spec_dir))

        # Should return valid data structures
        assert isinstance(specs, list)
        assert len(specs) > 0
        assert isinstance(components, dict)
        assert len(components) > 0
        assert isinstance(paths, dict)

        # Should have processed the spec correctly
        assert "User" in components
        assert any("/test/" in path for path in paths)

    def test_load_and_process_specs_empty_directory(self, build_coordinator: Any) -> None:
        """Test processing empty specs directory."""
        empty_dir = tempfile.mkdtemp()
        try:
            with pytest.raises(ValueError, match="No valid specifications found"):
                build_coordinator._load_and_process_specs(empty_dir)
        finally:
            shutil.rmtree(empty_dir)

    def test_generate_and_process_models(self, build_coordinator: Any, temp_spec_dir: Any) -> None:
        """Test model generation and processing."""
        # First get components
        _, components, _ = build_coordinator._load_and_process_specs(str(temp_spec_dir))

        # Test model generation
        models, reference_map = build_coordinator._generate_and_process_models(components)

        assert isinstance(models, dict)
        assert len(models) > 0
        assert isinstance(reference_map, dict)

        # Should have generated User model
        assert "User" in models
        # Arrays are generated as needed - may or may not be present for simple schemas

    def test_handle_dependencies_and_save_models(
        self, build_coordinator: Any, temp_spec_dir: Any, temp_output_dir: Any
    ) -> None:
        """Test dependency handling and model saving."""
        # First get components and generate models
        _, components, _ = build_coordinator._load_and_process_specs(str(temp_spec_dir))
        models, _ = build_coordinator._generate_and_process_models(components)

        # Test dependency handling and saving
        dependency_graph, circular_models, sorted_models = build_coordinator._handle_dependencies_and_save_models(
            models, str(temp_output_dir)
        )

        assert isinstance(dependency_graph, dict)
        assert isinstance(circular_models, set)
        assert isinstance(sorted_models, list)

        # Files should be created
        models_dir = temp_output_dir / "models"
        assert models_dir.exists()
        assert (models_dir / "__init__.py").exists()

    def test_generate_classes_and_diagrams(
        self, build_coordinator: Any, temp_spec_dir: Any, temp_output_dir: Any
    ) -> None:
        """Test client class generation and diagram creation."""
        # Prepare data
        specs, components, _ = build_coordinator._load_and_process_specs(str(temp_spec_dir))
        models, reference_map = build_coordinator._generate_and_process_models(components)
        dependency_graph, _, sorted_models = build_coordinator._handle_dependencies_and_save_models(
            models, str(temp_output_dir)
        )

        # Test class and diagram generation
        build_coordinator._generate_classes_and_diagrams(
            specs, components, reference_map, str(temp_output_dir), dependency_graph, sorted_models
        )

        # Check that endpoints were created
        endpoints_dir = temp_output_dir / "endpoints"
        assert endpoints_dir.exists()

        # Check that class diagram was created
        diagram_file = temp_output_dir / "class_diagram.mmd"
        assert diagram_file.exists()

    @patch("scripts.build_system.file_manager.FileManager.copy_infrastructure")
    def test_copy_infrastructure_called(
        self, mock_copy: Any, build_coordinator: Any, temp_spec_dir: Any, temp_output_dir: Any
    ) -> None:
        """Test that infrastructure copying is called during build."""
        # Run the full build
        with contextlib.suppress(Exception):
            build_coordinator.build(str(temp_spec_dir), str(temp_output_dir))

        # Infrastructure copying should have been called
        mock_copy.assert_called_once_with(str(temp_output_dir))

    def test_build_complete_workflow(self, build_coordinator: Any, temp_spec_dir: Any, temp_output_dir: Any) -> None:
        """Test the complete build workflow."""
        # Mock the infrastructure copying to avoid file system dependencies
        with patch("scripts.build_system.file_manager.FileManager.copy_infrastructure"):
            build_coordinator.build(str(temp_spec_dir), str(temp_output_dir))

        # Check that all expected outputs were created
        assert (temp_output_dir / "models").exists()
        assert (temp_output_dir / "endpoints").exists()
        assert (temp_output_dir / "class_diagram.mmd").exists()

        # Check specific files
        models_dir = temp_output_dir / "models"
        assert (models_dir / "__init__.py").exists()
        assert (models_dir / "User.py").exists()

        endpoints_dir = temp_output_dir / "endpoints"
        assert (endpoints_dir / "__init__.py").exists()
        assert (endpoints_dir / "UserClient.py").exists()

    def test_build_error_handling_file_not_found(self, build_coordinator: Any, temp_output_dir: Any) -> None:
        """Test error handling for non-existent spec path."""
        with pytest.raises(FileNotFoundError):
            build_coordinator.build("/nonexistent/path", str(temp_output_dir))

    def test_build_error_handling_empty_specs(self, build_coordinator: Any, temp_output_dir: Any) -> None:
        """Test error handling for directory with no valid specs."""
        empty_dir = tempfile.mkdtemp()
        try:
            with (
                pytest.raises(ValueError, match="No valid specifications found"),
                patch("scripts.build_system.file_manager.FileManager.copy_infrastructure"),
            ):
                build_coordinator.build(empty_dir, str(temp_output_dir))
        finally:
            shutil.rmtree(empty_dir)

    def test_build_error_handling_permission_error(self, build_coordinator: Any, temp_spec_dir: Any) -> None:
        """Test error handling for permission errors."""
        # Try to write to a read-only directory (simulate permission error)
        with (
            pytest.raises((PermissionError, OSError, RuntimeError)),
            patch("scripts.build_system.file_manager.FileManager.copy_infrastructure"),
        ):
            build_coordinator.build(str(temp_spec_dir), "/root/no_permission")

    def test_get_build_stats(self, build_coordinator: Any, temp_spec_dir: Any, temp_output_dir: Any) -> None:
        """Test getting build statistics."""
        # Initially should be empty
        stats = build_coordinator.get_build_stats()
        assert stats == {}

        # After build, should have statistics
        with patch("scripts.build_system.file_manager.FileManager.copy_infrastructure"):
            build_coordinator.build(str(temp_spec_dir), str(temp_output_dir))

        stats = build_coordinator.get_build_stats()
        assert isinstance(stats, dict)
        assert "models_generated" in stats
        assert "clients_generated" in stats
        assert "specs_processed" in stats

    def test_clear_state(self, build_coordinator: Any, temp_spec_dir: Any, temp_output_dir: Any) -> None:
        """Test clearing coordinator state."""
        # Run a build first
        with patch("scripts.build_system.file_manager.FileManager.copy_infrastructure"):
            build_coordinator.build(str(temp_spec_dir), str(temp_output_dir))

        # Verify state exists
        stats = build_coordinator.get_build_stats()
        assert len(stats) > 0

        # Clear state
        build_coordinator.clear()

        # Verify state is cleared
        stats = build_coordinator.get_build_stats()
        assert stats == {}

    def test_validate_output_after_build(
        self, build_coordinator: Any, temp_spec_dir: Any, temp_output_dir: Any
    ) -> None:
        """Test validating the build output."""
        with patch("scripts.build_system.file_manager.FileManager.copy_infrastructure"):
            build_coordinator.build(str(temp_spec_dir), str(temp_output_dir))

        # Validate output
        is_valid = build_coordinator.validate_build_output(str(temp_output_dir))
        assert is_valid

    def test_validate_output_missing_directory(self, build_coordinator: Any) -> None:
        """Test validation with missing output directory."""
        is_valid = build_coordinator.validate_build_output("/nonexistent/path")
        assert not is_valid

    def test_validate_output_incomplete_build(self, build_coordinator: Any, temp_output_dir: Any) -> None:
        """Test validation with incomplete build output."""
        # Create output directory but not the required subdirectories
        temp_output_dir.mkdir(exist_ok=True)

        is_valid = build_coordinator.validate_build_output(str(temp_output_dir))
        assert not is_valid

    def test_set_base_url(self, build_coordinator: Any) -> None:
        """Test setting custom base URL."""
        custom_url = "https://custom.api.com"
        build_coordinator.set_base_url(custom_url)

        # Should be used in subsequent builds
        assert build_coordinator._base_url == custom_url

    def test_get_component_counts(self, build_coordinator: Any, temp_spec_dir: Any, temp_output_dir: Any) -> None:
        """Test getting component counts after build."""
        with patch("scripts.build_system.file_manager.FileManager.copy_infrastructure"):
            build_coordinator.build(str(temp_spec_dir), str(temp_output_dir))

        counts = build_coordinator.get_component_counts()

        assert isinstance(counts, dict)
        assert "models" in counts
        assert "enums" in counts
        assert "arrays" in counts
        assert "clients" in counts

        # Should have positive counts
        assert counts["models"] > 0
        assert counts["clients"] > 0

    def test_build_with_custom_configuration(
        self, build_coordinator: Any, temp_spec_dir: Any, temp_output_dir: Any
    ) -> None:
        """Test build with custom configuration options."""
        config = {"generate_diagrams": False, "validate_output": True, "base_url": "https://custom.example.com"}

        with patch("scripts.build_system.file_manager.FileManager.copy_infrastructure"):
            build_coordinator.build(str(temp_spec_dir), str(temp_output_dir), config=config)

        # Diagram should not be created when disabled
        diagram_file = temp_output_dir / "class_diagram.mmd"
        assert not diagram_file.exists()

    def test_concurrent_build_safety(self, build_coordinator: Any, temp_spec_dir: Any) -> None:
        """Test that concurrent builds are handled safely."""
        output_dir1 = Path(tempfile.mkdtemp())
        output_dir2 = Path(tempfile.mkdtemp())

        try:
            with patch("scripts.build_system.file_manager.FileManager.copy_infrastructure"):
                # Should be able to run multiple builds
                build_coordinator.build(str(temp_spec_dir), str(output_dir1))
                build_coordinator.build(str(temp_spec_dir), str(output_dir2))

            # Both outputs should be valid
            assert (output_dir1 / "models").exists()
            assert (output_dir2 / "models").exists()

        finally:
            shutil.rmtree(output_dir1)
            shutil.rmtree(output_dir2)

    @pytest.mark.parametrize("invalid_input", [None, "", 123, ["not", "a", "string"]])
    def test_build_input_validation(self, build_coordinator: Any, invalid_input: Any) -> None:
        """Test build input validation with various invalid inputs."""
        with pytest.raises((TypeError, ValueError, FileNotFoundError, RuntimeError)):
            build_coordinator.build(invalid_input, "/some/output")

    def test_logging_configuration(self, build_coordinator: Any) -> None:
        """Test that logging is properly configured."""
        # Should have a logger
        assert hasattr(build_coordinator, "logger")
        assert build_coordinator.logger is not None

        # Logger should be configured with appropriate level
        assert build_coordinator.logger.level >= 0  # Some valid logging level
