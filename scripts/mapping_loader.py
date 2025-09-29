"""
Mapping loader for TfL API type mappings.

This module provides functions to load and access the structured JSON mappings
that replace the legacy Python mappings.
"""

import json
from pathlib import Path
from typing import Any

import jsonschema


class MappingLoader:
    """Loader for TfL API mappings with schema validation."""

    def __init__(self, data_file: Path | None = None, schema_file: Path | None = None):
        """Initialize the mapping loader.

        Args:
            data_file: Path to the mappings JSON file
            schema_file: Path to the JSON schema file
        """
        self._data_file = data_file or self._get_default_data_file()
        self._schema_file = schema_file or self._get_default_schema_file()
        self._mappings_data: dict[str, Any] | None = None
        self._schema: dict[str, Any] | None = None

    def _get_default_data_file(self) -> Path:
        """Get the default path to the mappings data file."""
        return Path(__file__).parent.parent / "data" / "tfl_mappings.json"

    def _get_default_schema_file(self) -> Path:
        """Get the default path to the schema file."""
        return Path(__file__).parent.parent / "schemas" / "tfl_mappings_schema.json"

    def _load_schema(self) -> dict[str, Any]:
        """Load and cache the JSON schema."""
        if self._schema is None:
            with open(self._schema_file, encoding="utf-8") as f:
                self._schema = json.load(f)
        assert self._schema is not None  # mypy assertion: schema is loaded
        return self._schema

    def _load_data(self) -> dict[str, Any]:
        """Load and cache the mappings data."""
        if self._mappings_data is None:
            with open(self._data_file, encoding="utf-8") as f:
                self._mappings_data = json.load(f)
        assert self._mappings_data is not None  # mypy assertion: data is loaded
        return self._mappings_data

    def validate(self) -> bool:
        """Validate the mappings data against the schema.

        Returns:
            True if validation passes

        Raises:
            ValidationError: If validation fails
        """
        schema = self._load_schema()
        data = self._load_data()
        jsonschema.validate(instance=data, schema=schema)
        return True

    def get_api_mappings(self, api_name: str) -> dict[str, str]:
        """Get type mappings for a specific API.

        Args:
            api_name: Name of the API (e.g., "Line", "Journey")

        Returns:
            Dictionary of type mappings for the API

        Raises:
            KeyError: If API not found
        """
        data = self._load_data()
        if api_name not in data["apis"]:
            raise KeyError(f"API '{api_name}' not found in mappings")

        return data["apis"][api_name]["mappings"]

    def get_api_response_mappings(self, api_name: str) -> dict[str, str]:
        """Get response mappings for a specific API.

        Args:
            api_name: Name of the API (e.g., "Line", "Journey")

        Returns:
            Dictionary of response mappings for the API

        Raises:
            KeyError: If API not found
        """
        data = self._load_data()
        if api_name not in data["apis"]:
            raise KeyError(f"API '{api_name}' not found in mappings")

        api_data = data["apis"][api_name]
        return api_data.get("response_mappings", {})

    def get_all_mappings(self, api_name: str) -> dict[str, str]:
        """Get combined type and response mappings for a specific API.

        Args:
            api_name: Name of the API (e.g., "Line", "Journey")

        Returns:
            Dictionary combining both type and response mappings

        Raises:
            KeyError: If API not found
        """
        type_mappings = self.get_api_mappings(api_name)
        response_mappings = self.get_api_response_mappings(api_name)

        # Combine both mappings using union operator
        return type_mappings | response_mappings

    def get_legacy_format(self) -> dict[str, dict[str, str]]:
        """Get mappings in the legacy Python format for backward compatibility.

        Returns:
            Dictionary in the same format as the old tfl_mappings variable
        """
        data = self._load_data()
        legacy_mappings = {}

        for api_name, api_data in data["apis"].items():
            # Combine mappings using union operator
            api_mappings = api_data["mappings"]
            if "response_mappings" in api_data:
                api_mappings = api_mappings | api_data["response_mappings"]
            legacy_mappings[api_name] = api_mappings

        return legacy_mappings

    def list_apis(self) -> list[str]:
        """Get list of all available API names.

        Returns:
            List of API names
        """
        data = self._load_data()
        return list(data["apis"].keys())

    def get_metadata(self) -> dict[str, Any]:
        """Get metadata about the mappings.

        Returns:
            Dictionary containing version, last_updated, and source info
        """
        data = self._load_data()
        return {"version": data["version"], "last_updated": data["last_updated"], "source": data["source"]}


# Convenience functions for backward compatibility
def load_tfl_mappings() -> dict[str, dict[str, str]]:
    """Load TfL mappings in legacy format.

    This function provides backward compatibility with the old mappings.py format.

    Returns:
        Dictionary in the same format as the old tfl_mappings variable
    """
    loader = MappingLoader()
    return loader.get_legacy_format()


def get_api_mappings(api_name: str) -> dict[str, str]:
    """Get mappings for a specific API.

    Args:
        api_name: Name of the API

    Returns:
        Dictionary of mappings for the API
    """
    loader = MappingLoader()
    return loader.get_all_mappings(api_name)


# Global instance for convenience
_default_loader = None


def get_default_loader() -> MappingLoader:
    """Get the default mapping loader instance."""
    global _default_loader
    if _default_loader is None:
        _default_loader = MappingLoader()
    return _default_loader
