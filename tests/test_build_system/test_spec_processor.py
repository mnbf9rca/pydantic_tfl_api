"""Tests for SpecProcessor class that handles OpenAPI specification loading and preprocessing."""

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import pytest

from scripts.build_system.spec_processor import SpecProcessor


class TestSpecProcessor:
    """Test the SpecProcessor class for OpenAPI specification handling."""

    @pytest.fixture
    def spec_processor(self) -> Any:
        """Create a SpecProcessor instance for testing."""
        return SpecProcessor()

    @pytest.fixture
    def temp_dir(self) -> Any:
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_spec_data(self) -> Any:
        """Create sample OpenAPI specification data."""
        return {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "servers": [{"url": "https://api.example.com/v1/test"}],
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
                        "required": ["id"],
                    },
                    "Profile-Data": {  # Test name sanitization
                        "type": "object",
                        "properties": {"userId": {"$ref": "#/components/schemas/User"}, "bio": {"type": "string"}},
                    },
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
                },
                "/users/{id}": {
                    "get": {
                        "operationId": "getUserById",
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                        "responses": {
                            "200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}
                        },
                    }
                },
            },
        }

    @pytest.fixture
    def create_spec_files(self, temp_dir: Any, sample_spec_data: Any) -> Any:
        """Create sample specification files in temp directory."""
        spec1 = sample_spec_data.copy()
        spec1["info"]["title"] = "API One"

        spec2 = sample_spec_data.copy()
        spec2["info"]["title"] = "API Two"
        spec2["servers"] = [{"url": "https://api.example.com/v1/other"}]

        spec1_file = temp_dir / "api1.json"
        spec2_file = temp_dir / "api2.json"

        with open(spec1_file, "w") as f:
            json.dump(spec1, f)

        with open(spec2_file, "w") as f:
            json.dump(spec2, f)

        # Create a non-JSON file to test filtering
        non_json_file = temp_dir / "readme.txt"
        non_json_file.write_text("This is not a JSON file")

        return [spec1_file, spec2_file, non_json_file]

    def test_init_creates_empty_state(self, spec_processor: Any) -> None:
        """Test that SpecProcessor initializes with empty state."""
        assert hasattr(spec_processor, "_specs")
        assert hasattr(spec_processor, "_combined_components")
        assert hasattr(spec_processor, "_combined_paths")
        assert hasattr(spec_processor, "_pydantic_names")

        assert spec_processor._specs == []
        assert spec_processor._combined_components == {}
        assert spec_processor._combined_paths == {}
        assert spec_processor._pydantic_names == {}

    def test_load_specs_from_directory(self, spec_processor: Any, temp_dir: Any, create_spec_files: Any) -> None:
        """Test loading specification files from a directory."""
        specs = spec_processor.load_specs(str(temp_dir))

        # Should load only JSON files
        assert len(specs) == 2
        assert all(isinstance(spec, dict) for spec in specs)
        assert all("openapi" in spec for spec in specs)

    def test_load_specs_empty_directory(self, spec_processor: Any, temp_dir: Any) -> None:
        """Test loading specs from empty directory."""
        specs = spec_processor.load_specs(str(temp_dir))
        assert specs == []

    def test_load_specs_nonexistent_directory(self, spec_processor: Any) -> None:
        """Test loading specs from non-existent directory."""
        with pytest.raises(FileNotFoundError):
            spec_processor.load_specs("/nonexistent/path")

    def test_get_api_name(self, spec_processor: Any, sample_spec_data: Any) -> None:
        """Test extracting API name from specification."""
        api_name = spec_processor.get_api_name(sample_spec_data)
        assert api_name == "Test API"

    def test_sanitize_name_functionality(self, spec_processor: Any) -> None:
        """Test name sanitization functionality."""
        # Test basic sanitization
        assert spec_processor.sanitize_name("user-profile") == "Profile"
        assert spec_processor.sanitize_name("user_data") == "Data"
        assert spec_processor.sanitize_name("SimpleModel") == "SimpleModel"

        # Test prefix handling - only needed for actual keywords or leading digits
        assert spec_processor.sanitize_name("123model") == "Model_123model"
        assert spec_processor.sanitize_name("class") == "Class"  # CamelCase makes it non-keyword

    def test_update_refs_basic(self, spec_processor: Any) -> None:
        """Test updating $ref values in a simple object."""
        obj = {"properties": {"user": {"$ref": "#/components/schemas/User-Data"}}}
        entity_mapping = {"User-Data": "UserData"}

        spec_processor.update_refs(obj, entity_mapping)

        assert obj["properties"]["user"]["$ref"] == "#/components/schemas/UserData"

    def test_update_refs_nested(self, spec_processor: Any) -> None:
        """Test updating $ref values in nested objects."""
        obj: dict[str, Any] = {
            "allOf": [
                {"$ref": "#/components/schemas/Base-Model"},
                {"properties": {"child": {"$ref": "#/components/schemas/Child-Model"}}},
            ]
        }
        entity_mapping = {"Base-Model": "BaseModel", "Child-Model": "ChildModel"}

        spec_processor.update_refs(obj, entity_mapping)

        assert obj["allOf"][0]["$ref"] == "#/components/schemas/BaseModel"
        assert obj["allOf"][1]["properties"]["child"]["$ref"] == "#/components/schemas/ChildModel"

    def test_update_refs_array(self, spec_processor: Any) -> None:
        """Test updating $ref values in arrays."""
        obj = [{"$ref": "#/components/schemas/Model-One"}, {"$ref": "#/components/schemas/Model-Two"}]
        entity_mapping = {"Model-One": "ModelOne", "Model-Two": "ModelTwo"}

        spec_processor.update_refs(obj, entity_mapping)

        assert obj[0]["$ref"] == "#/components/schemas/ModelOne"
        assert obj[1]["$ref"] == "#/components/schemas/ModelTwo"

    def test_update_entities(self, spec_processor: Any) -> None:
        """Test updating entity names in a specification."""
        spec: dict[str, Any] = {
            "components": {
                "schemas": {
                    "User-Profile": {
                        "type": "object",
                        "properties": {"user": {"$ref": "#/components/schemas/User-Data"}},
                    },
                    "User-Data": {"type": "object", "properties": {"id": {"type": "string"}}},
                }
            }
        }

        # Mock the tfl_mappings for this test
        api_name = "Test API"
        pydantic_names: dict[str, str] = {}

        # Simulate entity mapping
        spec_processor._entity_mappings = {api_name: {"User-Profile": "UserProfile", "User-Data": "UserData"}}

        spec_processor.update_entities(spec, api_name, pydantic_names)

        # Check that entity names were updated
        assert "UserProfile" in spec["components"]["schemas"]
        assert "UserData" in spec["components"]["schemas"]
        assert "User-Profile" not in spec["components"]["schemas"]
        assert "User-Data" not in spec["components"]["schemas"]

        # Check that references were updated
        user_ref = spec["components"]["schemas"]["UserProfile"]["properties"]["user"]["$ref"]
        assert "UserData" in user_ref

    def test_combine_components_and_paths(self, spec_processor: Any, temp_dir: Any, create_spec_files: Any) -> None:
        """Test combining components and paths from multiple specifications."""
        specs = spec_processor.load_specs(str(temp_dir))
        pydantic_names: dict[str, str] = {}

        combined_components, combined_paths = spec_processor.combine_components_and_paths(specs, pydantic_names)

        # Should combine components from all specs
        assert isinstance(combined_components, dict)
        assert len(combined_components) > 0

        # Should combine paths from all specs
        assert isinstance(combined_paths, dict)
        assert len(combined_paths) > 0

        # Check that paths have API-specific prefixes
        path_keys = list(combined_paths.keys())
        assert any("/test/" in path for path in path_keys)
        assert any("/other/" in path for path in path_keys)

    def test_create_array_types_from_paths(self, spec_processor: Any, sample_spec_data: Any) -> None:
        """Test creating array types from API paths."""
        paths = sample_spec_data["paths"]
        components = sample_spec_data["components"]["schemas"]

        array_types = spec_processor.create_array_types_from_model_paths(paths, components)

        # Should create array type for User model
        assert len(array_types) > 0

        # Check for UserArray
        user_array_key = None
        for key in array_types:
            if "User" in key and "Array" in key:
                user_array_key = key
                break

        assert user_array_key is not None
        assert array_types[user_array_key]["type"] == "array"
        assert "$ref" in array_types[user_array_key]["items"]

    def test_get_array_model_name(self, spec_processor: Any) -> None:
        """Test generating array model names."""
        assert spec_processor.get_array_model_name("User") == "UserArray"
        assert spec_processor.get_array_model_name("Profile-Data") == "DataArray"

    def test_create_openapi_array_type(self, spec_processor: Any) -> None:
        """Test creating OpenAPI array type definition."""
        model_ref = "#/components/schemas/User"
        array_type = spec_processor.create_openapi_array_type(model_ref)

        assert array_type["type"] == "array"
        assert array_type["items"]["$ref"] == model_ref

    def test_process_specs_complete_workflow(self, spec_processor: Any, temp_dir: Any, create_spec_files: Any) -> None:
        """Test the complete specification processing workflow."""
        specs = spec_processor.process_specs(str(temp_dir))

        # Should return processed specs
        assert isinstance(specs, tuple)
        assert len(specs) == 3  # specs, components, paths

        loaded_specs, combined_components, combined_paths = specs

        # Verify all parts are present
        assert isinstance(loaded_specs, list)
        assert len(loaded_specs) > 0
        assert isinstance(combined_components, dict)
        assert isinstance(combined_paths, dict)

    def test_get_specs(self, spec_processor: Any, temp_dir: Any, create_spec_files: Any) -> None:
        """Test getting loaded specifications."""
        # Initially should be empty
        assert spec_processor.get_specs() == []

        # After processing
        spec_processor.process_specs(str(temp_dir))
        specs = spec_processor.get_specs()

        assert isinstance(specs, list)
        assert len(specs) > 0

    def test_get_combined_components(self, spec_processor: Any, temp_dir: Any, create_spec_files: Any) -> None:
        """Test getting combined components."""
        # Initially should be empty
        assert spec_processor.get_combined_components() == {}

        # After processing
        spec_processor.process_specs(str(temp_dir))
        components = spec_processor.get_combined_components()

        assert isinstance(components, dict)
        assert len(components) > 0

    def test_get_combined_paths(self, spec_processor: Any, temp_dir: Any, create_spec_files: Any) -> None:
        """Test getting combined paths."""
        # Initially should be empty
        assert spec_processor.get_combined_paths() == {}

        # After processing
        spec_processor.process_specs(str(temp_dir))
        paths = spec_processor.get_combined_paths()

        assert isinstance(paths, dict)
        assert len(paths) > 0

    def test_get_pydantic_names(self, spec_processor: Any, temp_dir: Any, create_spec_files: Any) -> None:
        """Test getting pydantic name mappings."""
        # Initially should be empty
        assert spec_processor.get_pydantic_names() == {}

        # After processing (may or may not have mappings depending on entity mapping)
        spec_processor.process_specs(str(temp_dir))
        names = spec_processor.get_pydantic_names()

        assert isinstance(names, dict)

    def test_clear_state(self, spec_processor: Any, temp_dir: Any, create_spec_files: Any) -> None:
        """Test clearing processor state."""
        # Process some specs first
        spec_processor.process_specs(str(temp_dir))

        # Verify state is populated
        assert len(spec_processor.get_specs()) > 0
        assert len(spec_processor.get_combined_components()) > 0

        # Clear state
        spec_processor.clear()

        # Verify state is cleared
        assert spec_processor.get_specs() == []
        assert spec_processor.get_combined_components() == {}
        assert spec_processor.get_combined_paths() == {}
        assert spec_processor.get_pydantic_names() == {}

    def test_validate_spec_structure(self, spec_processor: Any) -> None:
        """Test validation of OpenAPI specification structure."""
        # Valid spec
        valid_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "components": {"schemas": {}},
            "paths": {},
        }
        assert spec_processor.validate_spec(valid_spec)

        # Invalid spec (missing required fields)
        invalid_spec = {"openapi": "3.0.0"}
        assert not spec_processor.validate_spec(invalid_spec)

    def test_error_handling_malformed_json(self, spec_processor: Any, temp_dir: Any) -> None:
        """Test handling of malformed JSON files."""
        # Create a malformed JSON file
        bad_file = temp_dir / "bad.json"
        bad_file.write_text("{invalid json content")

        # Should handle the error gracefully
        specs = spec_processor.load_specs(str(temp_dir))
        # Should skip the malformed file and return empty list
        assert specs == []
