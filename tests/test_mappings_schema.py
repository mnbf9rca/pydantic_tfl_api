"""
Tests for TfL mappings schema validation.

This replaces the brittle string-based tests with robust schema validation.
"""

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator, ValidationError, validate


class TestTflMappingsSchema:
    """Test suite for TfL mappings schema validation."""

    @pytest.fixture(scope="class")
    def schema(self) -> Any:
        """Load the JSON schema for TfL mappings."""
        schema_path = Path(__file__).parent.parent / "schemas" / "tfl_mappings_schema.json"
        with open(schema_path, encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture(scope="class")
    def mappings_data(self) -> Any:
        """Load the TfL mappings JSON data."""
        mappings_path = Path(__file__).parent.parent / "data" / "tfl_mappings.json"
        with open(mappings_path, encoding="utf-8") as f:
            return json.load(f)

    def test_schema_is_valid(self, schema: Any) -> None:
        """Test that the schema itself is valid JSON Schema."""
        # Validate the schema is a valid Draft 7 JSON Schema
        Draft7Validator.check_schema(schema)

    def test_mappings_conform_to_schema(self, schema: Any, mappings_data: Any) -> None:
        """Test that the mappings data conforms to the schema."""
        validate(instance=mappings_data, schema=schema)

    def test_required_fields_present(self, mappings_data: Any) -> None:
        """Test that all required top-level fields are present."""
        required_fields = ["version", "last_updated", "source", "apis"]
        missing_fields = [field for field in required_fields if field not in mappings_data]
        assert not missing_fields, f"Required fields missing from mappings: {missing_fields}"

    def test_version_format(self, mappings_data: Any) -> None:
        """Test that version follows semantic versioning."""
        version = mappings_data["version"]
        assert isinstance(version, str), "Version must be a string"
        # Check semantic version format (x.y.z)
        parts = version.split(".")
        assert len(parts) == 3, f"Version '{version}' must have 3 parts (x.y.z)"
        non_numeric_parts = [part for part in parts if not part.isdigit()]
        assert not non_numeric_parts, f"Version parts must be numeric, found: {non_numeric_parts}"

    def test_last_updated_format(self, mappings_data: Any) -> None:
        """Test that last_updated is a valid ISO 8601 timestamp."""
        from datetime import datetime

        timestamp = mappings_data["last_updated"]
        try:
            # Parse ISO 8601 timestamp
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"Invalid ISO 8601 timestamp: {timestamp}")

    def test_source_structure(self, mappings_data: Any) -> None:
        """Test that source has required fields and valid URL."""
        source = mappings_data["source"]
        assert "url" in source, "Source must have URL"
        assert "description" in source, "Source must have description"

        # Basic URL validation
        url = source["url"]
        assert url.startswith(("http://", "https://")), f"Invalid URL format: {url}"

    @pytest.mark.parametrize(
        "api_name",
        [
            "AccidentStats",
            "AirQuality",
            "BikePoint",
            "Journey",
            "Line",
            "Mode",
            "Place",
            "Road",
            "Search",
            "StopPoint",
            "Vehicle",
        ],
    )
    def test_known_apis_exist(self, mappings_data: Any, api_name: Any) -> None:
        """Test that expected APIs are present in mappings."""
        apis = mappings_data["apis"]
        assert api_name in apis, f"Expected API '{api_name}' not found in mappings"

    def test_api_structure(self, mappings_data: Any) -> None:
        """Test that each API has proper structure."""
        apis = mappings_data["apis"]

        # Check all APIs have mappings field
        apis_missing_mappings = [name for name, data in apis.items() if "mappings" not in data]
        assert not apis_missing_mappings, f"APIs missing mappings: {apis_missing_mappings}"

        # Check mappings are dictionaries
        apis_with_non_dict_mappings = [name for name, data in apis.items() if not isinstance(data["mappings"], dict)]
        assert not apis_with_non_dict_mappings, f"APIs with non-dict mappings: {apis_with_non_dict_mappings}"

        # Check description type when present
        apis_with_invalid_descriptions = [
            name for name, data in apis.items() if "description" in data and not isinstance(data["description"], str)
        ]
        assert (
            not apis_with_invalid_descriptions
        ), f"APIs with non-string descriptions: {apis_with_invalid_descriptions}"

        # Check response mappings type when present
        apis_with_invalid_response_mappings = [
            name
            for name, data in apis.items()
            if "response_mappings" in data and not isinstance(data["response_mappings"], dict)
        ]
        assert (
            not apis_with_invalid_response_mappings
        ), f"APIs with non-dict response_mappings: {apis_with_invalid_response_mappings}"

    def test_mapping_values_are_non_empty_strings(self, mappings_data: Any) -> None:
        """Test that all mapping values are non-empty strings."""
        apis = mappings_data["apis"]

        # Collect all validation errors using list comprehensions
        non_string_mappings = [
            f"{api_name}.{source_type}"
            for api_name, api_data in apis.items()
            for source_type, target_type in api_data["mappings"].items()
            if not isinstance(target_type, str)
        ]

        empty_mappings = [
            f"{api_name}.{source_type}"
            for api_name, api_data in apis.items()
            for source_type, target_type in api_data["mappings"].items()
            if isinstance(target_type, str) and len(target_type.strip()) == 0
        ]

        non_string_response_mappings = [
            f"{api_name}.{response_key}"
            for api_name, api_data in apis.items()
            if "response_mappings" in api_data
            for response_key, response_type in api_data["response_mappings"].items()
            if not isinstance(response_type, str)
        ]

        empty_response_mappings = [
            f"{api_name}.{response_key}"
            for api_name, api_data in apis.items()
            if "response_mappings" in api_data
            for response_key, response_type in api_data["response_mappings"].items()
            if isinstance(response_type, str) and len(response_type.strip()) == 0
        ]

        # Assert all validations
        assert not non_string_mappings, f"Non-string mapping values found: {non_string_mappings}"
        assert not empty_mappings, f"Empty mapping values found: {empty_mappings}"
        assert (
            not non_string_response_mappings
        ), f"Non-string response mapping values found: {non_string_response_mappings}"
        assert not empty_response_mappings, f"Empty response mapping values found: {empty_response_mappings}"

    def test_response_mapping_keys_follow_pattern(self, mappings_data: Any) -> None:
        """Test that response mapping keys follow expected patterns."""
        apis = mappings_data["apis"]

        # Collect all invalid response keys
        invalid_response_keys = [
            f"{api_name}.{response_key}"
            for api_name, api_data in apis.items()
            if "response_mappings" in api_data
            for response_key in api_data["response_mappings"]
            if "Get" not in response_key
        ]

        assert not invalid_response_keys, f"Response keys should contain 'Get': {invalid_response_keys}"

    def test_mappings_count(self, mappings_data: Any) -> None:
        """Test that we have a reasonable number of mappings."""
        apis = mappings_data["apis"]

        # Calculate total mappings using sum and generator expressions
        regular_mappings = sum(len(api_data["mappings"]) for api_data in apis.values())
        response_mappings = sum(
            len(api_data["response_mappings"]) for api_data in apis.values() if "response_mappings" in api_data
        )
        total_mappings = regular_mappings + response_mappings

        # Should have a substantial number of mappings (was 311 in original)
        assert total_mappings >= 300, f"Expected at least 300 mappings, found {total_mappings}"

    def test_no_duplicate_apis(self, mappings_data: Any) -> None:
        """Test that there are no duplicate API names."""
        apis = mappings_data["apis"]
        api_names = list(apis.keys())
        unique_names = set(api_names)
        assert len(api_names) == len(unique_names), "Duplicate API names found"

    def test_schema_validation_catches_errors(self, schema: Any) -> None:
        """Test that schema validation catches common errors."""
        # Test missing required field
        invalid_data_1 = {"version": "1.0.0"}
        with pytest.raises(ValidationError):
            validate(instance=invalid_data_1, schema=schema)

        # Test invalid version format
        invalid_data_2: dict[str, Any] = {
            "version": "invalid",
            "last_updated": "2025-09-28T18:32:38.586085Z",
            "source": {"url": "https://example.com", "description": "test"},
            "apis": {"TestAPI": {"mappings": {}}},
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_data_2, schema=schema)
