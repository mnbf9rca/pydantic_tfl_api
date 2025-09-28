"""
Tests for the build_models.py script functionality.
"""
import json
import tempfile
from pathlib import Path

import pytest

# Import from scripts package
from scripts.build_models import get_api_name, sanitize_name, update_refs


class TestSanitizeName:
    """Test the sanitize_name function."""

    def test_basic_sanitization(self):
        """Test basic name sanitization."""
        assert sanitize_name("simple-name") == "name"
        assert sanitize_name("Tfl.Api.Presentation.Entities.Mode") == "Mode"
        assert sanitize_name("Complex_Name_With_Underscores") == "Underscores"

    def test_keyword_handling(self):
        """Test Python keyword handling."""
        assert sanitize_name("class") == "Model_class"
        assert sanitize_name("from") == "Model_from"
        assert sanitize_name("if") == "Model_if"

    def test_digit_prefix_handling(self):
        """Test names starting with digits."""
        assert sanitize_name("123name") == "Model_123name"
        assert sanitize_name("9value") == "Model_9value"

    def test_custom_prefix(self):
        """Test custom prefix usage."""
        assert sanitize_name("class", prefix="Custom") == "Custom_class"
        assert sanitize_name("123name", prefix="Test") == "Test_123name"


class TestUpdateRefs:
    """Test the update_refs function."""

    def test_simple_ref_update(self):
        """Test simple reference updates."""
        obj = {"$ref": "#/components/schemas/OldName"}
        entity_mapping = {"OldName": "NewName"}
        update_refs(obj, entity_mapping)
        assert obj["$ref"] == "#/components/schemas/NewName"

    def test_nested_ref_update(self):
        """Test nested reference updates."""
        obj = {
            "properties": {
                "field": {"$ref": "#/components/schemas/OldName"}
            }
        }
        entity_mapping = {"OldName": "NewName"}
        update_refs(obj, entity_mapping)
        assert obj["properties"]["field"]["$ref"] == "#/components/schemas/NewName"

    def test_array_ref_update(self):
        """Test reference updates in arrays."""
        obj = {
            "items": [
                {"$ref": "#/components/schemas/OldName"},
                {"other": "value"}
            ]
        }
        entity_mapping = {"OldName": "NewName"}
        update_refs(obj, entity_mapping)
        assert obj["items"][0]["$ref"] == "#/components/schemas/NewName"
        assert obj["items"][1]["other"] == "value"

    def test_deeply_nested_array_ref_update(self):
        """Test reference updates in deeply nested arrays."""
        obj = {
            "items": [
                [
                    {"$ref": "#/components/schemas/OldName"},
                    [
                        {"$ref": "#/components/schemas/OldName"},
                        {"other": "value"}
                    ]
                ],
                {"$ref": "#/components/schemas/OldName"}
            ]
        }
        entity_mapping = {"OldName": "NewName"}
        update_refs(obj, entity_mapping)
        assert obj["items"][0][0]["$ref"] == "#/components/schemas/NewName"
        assert obj["items"][0][1][0]["$ref"] == "#/components/schemas/NewName"
        assert obj["items"][0][1][1]["other"] == "value"
        assert obj["items"][1]["$ref"] == "#/components/schemas/NewName"

    def test_mixed_type_structures_ref_update(self):
        """Test reference updates in mixed-type structures (dicts, lists, primitives)."""
        obj = {
            "properties": {
                "array": [
                    {"$ref": "#/components/schemas/OldName"},
                    123,
                    "string",
                    {"nested": [{"$ref": "#/components/schemas/OldName"}]},
                    [],  # empty list
                ],
                "dict": {
                    "key": {"$ref": "#/components/schemas/OldName"},
                    "list": [
                        {"$ref": "#/components/schemas/OldName"},
                        {"other": "value"}
                    ],
                    "empty_list": [],
                    "empty_dict": {},
                }
            }
        }
        entity_mapping = {"OldName": "NewName"}
        update_refs(obj, entity_mapping)
        assert obj["properties"]["array"][0]["$ref"] == "#/components/schemas/NewName"
        assert obj["properties"]["array"][1] == 123
        assert obj["properties"]["array"][2] == "string"
        assert obj["properties"]["array"][3]["nested"][0]["$ref"] == "#/components/schemas/NewName"
        # Test empty containers are preserved
        assert obj["properties"]["array"][4] == []
        assert obj["properties"]["dict"]["key"]["$ref"] == "#/components/schemas/NewName"
        assert obj["properties"]["dict"]["list"][0]["$ref"] == "#/components/schemas/NewName"
        assert obj["properties"]["dict"]["list"][1]["other"] == "value"
        assert obj["properties"]["dict"]["empty_list"] == []
        assert obj["properties"]["dict"]["empty_dict"] == {}

    def test_update_refs_error_conditions(self):
        """Test update_refs handles error conditions gracefully."""
        entity_mapping = {"OldName": "NewName"}

        # Test with None input - should not crash
        update_refs(None, entity_mapping)

        # Test with non-dict, non-list input - should not crash
        update_refs("string", entity_mapping)
        update_refs(123, entity_mapping)

        # Test with malformed dict structure - should not crash
        malformed_obj = {"$ref": None}
        update_refs(malformed_obj, entity_mapping)

        # Test with empty entity mapping
        obj_with_ref = {"$ref": "#/components/schemas/OldName"}
        update_refs(obj_with_ref, {})
        # Should remain unchanged when no mapping exists
        assert obj_with_ref["$ref"] == "#/components/schemas/OldName"


class TestGetApiName:
    """Test the get_api_name function."""

    def test_api_name_extraction(self):
        """Test API name extraction from spec."""
        spec = {
            "info": {
                "title": "Test API",
                "version": "1.0"
            }
        }
        assert get_api_name(spec) == "Test API"

    def test_missing_info_section(self):
        """Test handling of missing info section."""
        spec = {}
        with pytest.raises(KeyError):
            get_api_name(spec)


class TestBuildModelsIntegration:
    """Integration tests for the build models functionality."""

    def create_minimal_openapi_spec(self, api_name="TestAPI"):
        """Create a minimal valid OpenAPI spec for testing."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": api_name,
                "version": "1.0.0"
            },
            "paths": {
                "/test": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/TestModel"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "TestModel": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "name": {
                                "type": "string"
                            }
                        }
                    }
                }
            }
        }

    def test_minimal_spec_processing(self):
        """Test processing of a minimal OpenAPI spec."""
        # This test ensures the basic flow works without external dependencies
        spec = self.create_minimal_openapi_spec()
        api_name = get_api_name(spec)
        assert api_name == "TestAPI"

        # Test that the spec structure is valid
        assert "components" in spec
        assert "schemas" in spec["components"]
        assert "TestModel" in spec["components"]["schemas"]

    def test_build_with_temp_directory(self):
        """Integration test with temporary files."""
        # Skip this test if external dependencies aren't available
        pytest.importorskip("scripts.build_models", reason="build_models module not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test spec file
            spec = self.create_minimal_openapi_spec()
            spec_file = Path(temp_dir) / "test_spec.json"

            with open(spec_file, 'w') as f:
                json.dump(spec, f)

            # This test verifies the file structure is correct
            # Full integration testing will be done in Phase 2.5
            assert spec_file.exists()
            assert json.loads(spec_file.read_text())["info"]["title"] == "TestAPI"


class TestMappingsImport:
    """Test that mappings can be imported successfully."""

    def _load_tfl_mappings_or_skip(self):
        """Helper to load TfL mappings or skip test if not available."""
        try:
            from scripts.mapping_loader import load_tfl_mappings
            return load_tfl_mappings()
        except ImportError as e:
            pytest.skip(f"mapping_loader module not available: {e}")

    def _validate_mapping_structure(self, api_mappings, api_name):
        """Helper to validate mapping structure without loops in test."""
        # Validate all mapping keys are strings
        invalid_keys = [k for k in api_mappings if not isinstance(k, str)]
        assert not invalid_keys, f"Non-string keys found in {api_name}: {invalid_keys}"

        # Validate all mapping values are strings
        invalid_values = [v for v in api_mappings.values() if not isinstance(v, str)]
        assert not invalid_values, f"Non-string values found in {api_name}: {invalid_values}"

    def test_mappings_import(self):
        """Test that mappings module imports successfully."""
        tfl_mappings = self._load_tfl_mappings_or_skip()
        assert isinstance(tfl_mappings, dict)
        assert len(tfl_mappings) > 0


    @pytest.mark.parametrize("api_name", ["AccidentStats", "AirQuality", "BikePoint", "Journey", "Line"])
    def test_known_api_mappings_structure(self, api_name):
        """Test the structure of specific TfL API mappings."""
        tfl_mappings = self._load_tfl_mappings_or_skip()

        # Validate API exists and get its mappings
        api_mappings = self._get_api_mappings_or_skip(tfl_mappings, api_name)
        assert isinstance(api_mappings, dict)

        # Test that all keys and values are strings using helper method
        self._validate_mapping_structure(api_mappings, api_name)

    def _get_api_mappings_or_skip(self, tfl_mappings, api_name):
        """Helper to get API mappings or skip test if not found."""
        if api_name not in tfl_mappings:
            pytest.skip(f"API '{api_name}' not found in mappings")
        return tfl_mappings[api_name]
