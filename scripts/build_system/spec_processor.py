"""OpenAPI specification loading and preprocessing functionality.

This module handles loading, validating, and processing OpenAPI specifications
for the TfL API client generation process.
"""

import json
import logging
import os
from typing import Any
from urllib.parse import urljoin

try:
    from ..mapping_loader import load_tfl_mappings
    from .utilities import sanitize_name
except ImportError:
    # Fallback for when run as script - need to add parent to path
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from build_system.utilities import sanitize_name  # type: ignore[import-not-found, no-redef]
    from mapping_loader import load_tfl_mappings  # type: ignore[import-not-found, no-redef]


class SpecProcessor:
    """Handles OpenAPI specification loading and preprocessing."""

    def __init__(self) -> None:
        """Initialize the SpecProcessor with empty state."""
        self._specs: list[dict[str, Any]] = []
        self._combined_components: dict[str, Any] = {}
        self._combined_paths: dict[str, Any] = {}
        self._pydantic_names: dict[str, str] = {}
        self._entity_mappings: dict[str, dict[str, str]] = {}

        # Load TfL mappings for entity updating
        try:
            tfl_mappings = load_tfl_mappings()
            self._entity_mappings = tfl_mappings
        except Exception as e:
            logging.warning(f"Failed to load TfL mappings: {e}")
            self._entity_mappings = {}

    def load_specs(self, folder_path: str) -> list[dict[str, Any]]:
        """Load OpenAPI specification files from a directory.

        Args:
            folder_path: Path to directory containing JSON spec files

        Returns:
            List of loaded OpenAPI specifications

        Raises:
            FileNotFoundError: If directory doesn't exist
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Directory not found: {folder_path}")

        specs = []
        try:
            for filename in os.listdir(folder_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            spec = json.load(f)
                            if self.validate_spec(spec):
                                specs.append(spec)
                            else:
                                logging.warning(f"Invalid spec structure in {filename}")
                    except json.JSONDecodeError as e:
                        logging.warning(f"Failed to parse JSON file {filename}: {e}")
                    except Exception as e:
                        logging.warning(f"Error loading {filename}: {e}")
        except Exception as e:
            logging.error(f"Error accessing directory {folder_path}: {e}")

        return specs

    def get_api_name(self, spec: dict[str, Any]) -> str:
        """Extract the API name from a specification.

        Args:
            spec: OpenAPI specification dictionary

        Returns:
            The API title from the spec
        """
        return spec["info"]["title"]

    def sanitize_name(self, name: str, prefix: str = "Model") -> str:
        """Sanitize names for Python class generation.

        Args:
            name: Name to sanitize
            prefix: Prefix for invalid names

        Returns:
            Sanitized name suitable for Python classes
        """
        return sanitize_name(name, prefix)

    def update_refs(self, obj: Any, entity_mapping: dict[str, str]) -> None:
        """Recursively update $ref values in an object.

        Args:
            obj: Object to update (can be dict, list, or other)
            entity_mapping: Mapping of old names to new names
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "$ref" and isinstance(value, str):
                    ref_name = value.split("/")[-1]
                    if ref_name in entity_mapping:
                        obj[key] = value.replace(ref_name, entity_mapping[ref_name])
                else:
                    self.update_refs(value, entity_mapping)
        elif isinstance(obj, list):
            for item in obj:
                self.update_refs(item, entity_mapping)

    def update_entities(self, spec: dict[str, Any], api_name: str, pydantic_names: dict[str, str]) -> None:
        """Update entity names in a specification based on mappings.

        Args:
            spec: OpenAPI specification to update
            api_name: Name of the API
            pydantic_names: Dictionary to track name mappings
        """
        if api_name not in self._entity_mappings:
            return

        entity_mapping = self._entity_mappings[api_name]
        components = spec.get("components", {}).get("schemas", {})

        # Sanitize old and new names to match how they will be used in the models
        sanitized_entity_mapping = {
            old_name: self.sanitize_name(new_name) for old_name, new_name in entity_mapping.items()
        }

        # Rename entities in the schema components
        for old_name, new_name in sanitized_entity_mapping.items():
            if old_name in components:
                components[new_name] = components.pop(old_name)
                pydantic_names[old_name] = new_name

        # Update references recursively in the spec
        self.update_refs(spec, sanitized_entity_mapping)

    def combine_components_and_paths(
        self, specs: list[dict[str, Any]], pydantic_names: dict[str, str]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Combine components and paths from multiple OpenAPI specifications.

        Args:
            specs: List of OpenAPI specifications
            pydantic_names: Dictionary to track name mappings

        Returns:
            Tuple of (combined_components, combined_paths)
        """
        combined_components = {}
        combined_paths = {}

        for spec in specs:
            api_name = self.get_api_name(spec)

            # Extract API path from server URL (same logic as original)
            servers = spec.get("servers", [{}])
            server_url = servers[0].get("url", "") if servers else ""
            url_parts = server_url.split("/", 3)
            api_path = f"/{url_parts[3]}" if len(url_parts) > 3 else ""

            logging.info(f"Processing {api_name}")
            self.update_entities(spec, api_name, pydantic_names)

            # Combine components
            combined_components.update(spec.get("components", {}).get("schemas", {}))

            # Combine paths with API-specific prefixes
            these_paths = spec.get("paths", {})
            for path, methods in these_paths.items():
                new_path = urljoin(f"{api_path}/", path.lstrip("/"))
                combined_paths[new_path] = methods

        return combined_components, combined_paths

    def create_array_types_from_model_paths(
        self, paths: dict[str, dict[str, Any]], components: dict[str, Any]
    ) -> dict[str, Any]:
        """Create array types based on API endpoint responses.

        Args:
            paths: OpenAPI paths dictionary
            components: OpenAPI components dictionary

        Returns:
            Dictionary of array type definitions
        """
        array_types = {}

        for path, methods in paths.items():
            for method, details in methods.items():
                operation_id = details.get("operationId")
                if not operation_id:
                    continue

                responses = details.get("responses", {})
                success_response = responses.get("200")
                if not success_response or "content" not in success_response:
                    continue

                try:
                    content = success_response["content"]
                    if "application/json" not in content:
                        continue

                    schema = content["application/json"].get("schema", {})
                    response_type = schema.get("type", "")

                    if response_type == "array":
                        items = schema.get("items", {})
                        model_ref = items.get("$ref", "")
                        if model_ref:
                            model_name = model_ref.split("/")[-1]
                            if model_name in components:
                                array_model_name = self.get_array_model_name(model_name)
                                array_types[array_model_name] = self.create_openapi_array_type(model_ref)
                except (KeyError, TypeError) as e:
                    logging.debug(f"Skipping path {path} method {method}: {e}")
                    continue

        return array_types

    def get_array_model_name(self, model_name: str) -> str:
        """Generate array model name from base model name.

        Args:
            model_name: Base model name

        Returns:
            Array model name
        """
        return f"{self.sanitize_name(model_name)}Array"

    def create_openapi_array_type(self, model_ref: str) -> dict[str, Any]:
        """Create OpenAPI array type definition.

        Args:
            model_ref: Reference to the model type

        Returns:
            OpenAPI array type definition
        """
        return {"type": "array", "items": {"$ref": model_ref}}

    def process_specs(self, folder_path: str) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
        """Process OpenAPI specifications from a directory.

        This is the main entry point that performs the complete workflow:
        1. Load specifications
        2. Combine components and paths
        3. Create array types

        Args:
            folder_path: Path to directory containing spec files

        Returns:
            Tuple of (loaded_specs, combined_components, combined_paths)
        """
        # Clear previous state
        self.clear()

        # Load specifications
        self._specs = self.load_specs(folder_path)

        # Combine components and paths
        self._combined_components, self._combined_paths = self.combine_components_and_paths(
            self._specs, self._pydantic_names
        )

        # Create array types from paths
        array_types = self.create_array_types_from_model_paths(self._combined_paths, self._combined_components)

        # Add array types to combined components
        self._combined_components.update(array_types)

        return self._specs, self._combined_components, self._combined_paths

    def validate_spec(self, spec: dict[str, Any]) -> bool:
        """Validate OpenAPI specification structure.

        Args:
            spec: OpenAPI specification to validate

        Returns:
            True if spec has valid structure, False otherwise
        """
        required_fields = ["openapi", "info", "components", "paths"]

        if not all(field in spec for field in required_fields):
            return False

        info = spec.get("info", {})
        if not isinstance(info, dict) or "title" not in info or "version" not in info:
            return False

        components = spec.get("components", {})
        if not isinstance(components, dict):
            return False

        paths = spec.get("paths", {})
        return isinstance(paths, dict)

    # Getters for accessing processed data
    def get_specs(self) -> list[dict[str, Any]]:
        """Get loaded specifications."""
        return self._specs

    def get_combined_components(self) -> dict[str, Any]:
        """Get combined components from all specs."""
        return self._combined_components

    def get_combined_paths(self) -> dict[str, Any]:
        """Get combined paths from all specs."""
        return self._combined_paths

    def get_pydantic_names(self) -> dict[str, str]:
        """Get pydantic name mappings."""
        return self._pydantic_names

    def clear(self) -> None:
        """Clear all internal state."""
        self._specs = []
        self._combined_components = {}
        self._combined_paths = {}
        self._pydantic_names = {}
