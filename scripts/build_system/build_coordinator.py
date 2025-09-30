"""BuildCoordinator orchestrates the entire build process for Pydantic models."""

import logging
import os
from pathlib import Path
from typing import Any

from scripts.build_system.client_generator import ClientGenerator
from scripts.build_system.dependency_resolver import DependencyResolver
from scripts.build_system.file_manager import FileManager
from scripts.build_system.model_builder import ModelBuilder
from scripts.build_system.spec_processor import SpecProcessor
from scripts.build_system.utilities import deduplicate_models, update_model_references


class BuildCoordinator:
    """Coordinates the entire build process for Pydantic models."""

    def __init__(self) -> None:
        """Initialize the BuildCoordinator with all required components."""
        self.logger = logging.getLogger(__name__)

        # Initialize build system components
        self.spec_processor = SpecProcessor()
        self.model_builder = ModelBuilder()
        self.dependency_resolver = DependencyResolver()
        self.file_manager = FileManager()
        self.client_generator = ClientGenerator()

        # Build state
        self._build_stats: dict[str, Any] = {}
        self._base_url = "https://api.tfl.gov.uk"

    def build(self, spec_path: str, output_path: str, config: dict[str, Any] | None = None) -> None:
        """
        Main orchestration method that coordinates the entire build process.

        Args:
            spec_path: Path to directory containing OpenAPI specifications
            output_path: Path to directory where generated code will be saved
            config: Optional configuration dictionary

        Raises:
            FileNotFoundError: If spec_path doesn't exist
            ValueError: If no valid specifications found
            PermissionError: If unable to write to output_path
            RuntimeError: For other build failures
        """
        try:
            self.logger.info(f"Starting build process from {spec_path} to {output_path}")

            # Apply configuration if provided
            if config:
                self._apply_config(config)

            # Clear any previous build state
            self._build_stats = {}

            # Step 1: Validate paths and setup
            self._validate_and_setup_paths(spec_path, output_path)

            # Step 2: Copy infrastructure files
            self.file_manager.copy_infrastructure(output_path)

            # Step 3: Load and process specifications
            specs, components, paths = self._load_and_process_specs(spec_path)

            # Step 4: Generate and process models
            models, reference_map = self._generate_and_process_models(components)

            # Step 5: Handle dependencies and save models
            dependency_graph, circular_models, sorted_models = self._handle_dependencies_and_save_models(
                models, output_path
            )

            # Step 6: Generate client classes and diagrams
            self._generate_classes_and_diagrams(
                specs, components, reference_map, output_path, dependency_graph, sorted_models, config
            )

            # Update build statistics
            self._build_stats.update(
                {
                    "models_generated": len(models),
                    "clients_generated": len(specs),
                    "specs_processed": len(specs),
                    "circular_dependencies": len(circular_models),
                    "total_dependencies": len(dependency_graph),
                }
            )

            self.logger.info(f"Build completed successfully. Generated {len(models)} models.")

        except FileNotFoundError as e:
            self.logger.error(f"File not found error: {e}")
            raise
        except ValueError as e:
            self.logger.error(f"Value error during build: {e}")
            raise
        except PermissionError as e:
            self.logger.error(f"Permission error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during build: {e}", exc_info=True)
            raise RuntimeError(f"Build failed: {e}") from e

    def _validate_and_setup_paths(self, spec_path: str, output_path: str) -> None:
        """Validate input paths and create output directory."""
        # Validate input types
        if not isinstance(spec_path, str):
            raise TypeError(f"spec_path must be a string, got {type(spec_path)}")
        if not isinstance(output_path, str):
            raise TypeError(f"output_path must be a string, got {type(output_path)}")

        if not spec_path:
            raise ValueError("spec_path cannot be empty")
        if not output_path:
            raise ValueError("output_path cannot be empty")

        if not os.path.exists(spec_path):
            raise FileNotFoundError(f"Specification path does not exist: {spec_path}")

        self.logger.info(f"Starting model generation from {spec_path} to {output_path}")
        os.makedirs(output_path, exist_ok=True)

    def _load_and_process_specs(self, spec_path: str) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
        """Load OpenAPI specs and process components and paths."""
        self.logger.info("Loading OpenAPI specs...")
        specs, components, paths = self.spec_processor.process_specs(spec_path)

        if not specs:
            raise ValueError(f"No valid specifications found in {spec_path}")

        return specs, components, paths

    def _generate_and_process_models(self, components: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
        """Generate Pydantic models and process them for deduplication."""
        self.logger.info("Generating Pydantic models...")

        # Use the new ModelBuilder class instead of the old function
        self.model_builder.create_pydantic_models(components)
        models = self.model_builder.get_models()

        # First deduplication pass: remove duplicate base models
        self.logger.info("Deduplicating models (first pass)...")
        deduplicated_models, reference_map = deduplicate_models(models)

        # Update model references to point to canonical models
        self.logger.info("Updating model references...")
        models = update_model_references(deduplicated_models, reference_map)

        # Second deduplication pass: remove duplicate array/composite models
        # that become identical after reference updates
        self.logger.info("Deduplicating models (second pass)...")
        final_models, additional_refs = deduplicate_models(models)

        # Merge reference maps
        reference_map.update(additional_refs)

        return final_models, reference_map

    def _handle_dependencies_and_save_models(
        self, models: dict[str, Any], output_path: str
    ) -> tuple[dict[str, set[str]], set[str], list[str]]:
        """Handle model dependencies and save models to files."""
        self.logger.info("Handling dependencies...")
        dependency_graph, circular_models, sorted_models = self.dependency_resolver.resolve_dependencies(models)

        # Get descriptions from model_builder
        model_descriptions = self.model_builder.get_model_descriptions()
        field_descriptions = self.model_builder.get_field_descriptions()

        # Save the models using FileManager
        self.logger.info("Saving models to files...")
        self.file_manager.save_models(
            models, output_path, dependency_graph, circular_models, sorted_models, model_descriptions, field_descriptions
        )

        return dependency_graph, circular_models, sorted_models

    def _generate_classes_and_diagrams(
        self,
        specs: list[dict[str, Any]],
        components: dict[str, Any],
        reference_map: dict[str, str],
        output_path: str,
        dependency_graph: dict[str, list[str]],
        sorted_models: list[str],
        config: dict[str, Any] | None = None,
    ) -> None:
        """Generate API classes and create documentation diagrams."""
        self.logger.info("Creating config and class files...")

        # Generate client classes with reference map for deduplication
        self.client_generator.save_classes(specs, output_path, self._base_url, reference_map)

        # Create class diagram if not disabled
        generate_diagrams = True
        if config and "generate_diagrams" in config:
            generate_diagrams = config["generate_diagrams"]

        if generate_diagrams:
            endpoints_path = os.path.join(output_path, "endpoints")

            # Generate combined class diagram (comprehensive view with all relationships)
            self.logger.info("Creating class diagram...")
            self.file_manager.create_mermaid_class_diagram(
                dependency_graph, sorted_models, os.path.join(output_path, "class_diagram.mmd"), endpoints_path
            )

            # Generate API mindmap (explorable API surface view with reuse indicators)
            self.logger.info("Creating API mindmap...")
            self.file_manager.create_mermaid_api_mindmap(endpoints_path, os.path.join(output_path, "api_mindmap.mmd"))

    def _apply_config(self, config: dict[str, Any]) -> None:
        """Apply configuration options."""
        if "base_url" in config:
            self.set_base_url(config["base_url"])

    def get_build_stats(self) -> dict[str, Any]:
        """Get build statistics."""
        return self._build_stats.copy()

    def clear(self) -> None:
        """Clear coordinator state."""
        self._build_stats = {}
        self.logger.info("Build coordinator state cleared")

    def validate_build_output(self, output_path: str) -> bool:
        """
        Validate that the build output is complete and correct.

        Args:
            output_path: Path to the build output directory

        Returns:
            True if build output is valid, False otherwise
        """
        try:
            output_dir = Path(output_path)

            # Check if output directory exists
            if not output_dir.exists():
                self.logger.warning(f"Output directory does not exist: {output_path}")
                return False

            # Check for required subdirectories
            required_dirs = ["models", "endpoints"]
            for required_dir in required_dirs:
                dir_path = output_dir / required_dir
                if not dir_path.exists():
                    self.logger.warning(f"Required directory missing: {required_dir}")
                    return False

                # Check for __init__.py in each directory
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    self.logger.warning(f"__init__.py missing in {required_dir}")
                    return False

            self.logger.info("Build output validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Error validating build output: {e}")
            return False

    def set_base_url(self, base_url: str) -> None:
        """Set the base URL for API clients."""
        self._base_url = base_url
        self.logger.info(f"Base URL set to: {base_url}")

    def get_component_counts(self) -> dict[str, int]:
        """
        Get counts of different component types after build.

        Returns:
            Dictionary with counts of models, enums, arrays, and clients
        """
        if not self._build_stats:
            return {"models": 0, "enums": 0, "arrays": 0, "clients": 0}

        # Extract component counts from build stats
        total_models = self._build_stats.get("models_generated", 0)
        clients = self._build_stats.get("clients_generated", 0)

        # For simple cases, just report what we have
        return {
            "models": total_models,
            "enums": 0,  # Would need more detailed tracking to count enums accurately
            "arrays": 0,  # Would need more detailed tracking to count arrays accurately
            "clients": clients,
        }
