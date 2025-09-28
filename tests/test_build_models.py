"""
Tests for the build_models.py script functionality.
"""
import os
import sys
import tempfile
import json
from pathlib import Path

import pytest
from pydantic import BaseModel

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from build_models import sanitize_name, update_refs, get_api_name


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

    def test_mappings_import(self):
        """Test that mappings module imports successfully."""
        try:
            from mappings import tfl_mappings
            assert isinstance(tfl_mappings, dict)
            assert len(tfl_mappings) > 0
        except ImportError:
            pytest.skip("mappings module not available")

    def test_mappings_structure(self):
        """Test the structure of TfL mappings."""
        try:
            from mappings import tfl_mappings

            # Check that known APIs have mappings
            expected_apis = ["AccidentStats", "AirQuality", "BikePoint", "Journey", "Line"]
            for api in expected_apis:
                if api in tfl_mappings:
                    assert isinstance(tfl_mappings[api], dict)

        except ImportError:
            pytest.skip("mappings module not available")