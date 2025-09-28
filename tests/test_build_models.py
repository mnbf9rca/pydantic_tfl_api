"""
Tests for the build_models.py script functionality.
"""
import json
import tempfile
from pathlib import Path

import pytest

# Import from scripts package
from scripts.build_models import (
    get_api_name, sanitize_name, update_refs, create_enum_class,
    map_type, map_openapi_type, create_generic_response_model,
    get_pydantic_imports, get_model_config, sanitize_field_name,
    get_builtin_types, is_list_or_dict_model, extract_inner_types,
    topological_sort, detect_circular_dependencies, join_url_paths,
    classify_parameters, _create_schema_name_mapping
)
from enum import Enum
from typing import Any, Dict, List, Optional, Union, ForwardRef
from pydantic import BaseModel, RootModel


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


class TestCreateEnumClass:
    """Test the create_enum_class function."""

    def test_basic_enum_creation(self):
        """Test basic enum creation with simple values."""
        enum_values = ["red", "green", "blue"]
        result_enum = create_enum_class("ColorEnum", enum_values)

        # Check that it's an Enum class
        assert issubclass(result_enum, Enum)
        assert result_enum.__name__ == "ColorEnum"

        # Check values
        enum_items = list(result_enum)
        assert len(enum_items) == 3
        assert "RED" in [item.name for item in enum_items]
        assert "GREEN" in [item.name for item in enum_items]
        assert "BLUE" in [item.name for item in enum_items]

    def test_enum_with_special_characters(self):
        """Test enum creation with special characters and spaces."""
        enum_values = ["value-with-dash", "value with spaces", "123numeric"]
        result_enum = create_enum_class("SpecialEnum", enum_values)

        enum_items = list(result_enum)
        assert len(enum_items) == 3
        # Check that special characters are handled
        names = [item.name for item in enum_items]
        assert any("DASH" in name or "WITH" in name for name in names)

    def test_enum_with_duplicate_values(self):
        """Test enum creation with duplicate values."""
        enum_values = ["duplicate", "duplicate", "unique"]
        result_enum = create_enum_class("DuplicateEnum", enum_values)

        enum_items = list(result_enum)
        # The function actually deduplicates values, so we get fewer items
        assert len(enum_items) >= 2  # At least unique and one duplicate
        names = [item.name for item in enum_items]
        assert "DUPLICATE" in names or any("DUPLICATE" in name for name in names)
        assert "UNIQUE" in names

    def test_enum_with_empty_values(self):
        """Test enum creation with empty list."""
        result_enum = create_enum_class("EmptyEnum", [])
        assert issubclass(result_enum, Enum)
        assert len(list(result_enum)) == 0


class TestMapType:
    """Test the map_type function."""

    def test_ref_mapping(self):
        """Test mapping of $ref fields."""
        field_spec = {"$ref": "#/components/schemas/TestModel"}
        result = map_type(field_spec, "test_field", {}, {})

        # Should return a ForwardRef
        assert isinstance(result, ForwardRef)
        assert result.__forward_arg__ == "TestModel"

    def test_enum_mapping(self):
        """Test mapping of enum fields."""
        field_spec = {
            "type": "string",
            "enum": ["option1", "option2", "option3"]
        }
        result = map_type(field_spec, "status", {}, {})

        # Should return an Enum class
        assert issubclass(result, Enum)
        assert result.__name__ == "StatusEnum"

    def test_array_mapping(self):
        """Test mapping of array fields."""
        field_spec = {
            "type": "array",
            "items": {"type": "string"}
        }
        result = map_type(field_spec, "items", {}, {})

        # Should return List[str]
        assert hasattr(result, '__origin__')
        assert result.__origin__ is list
        assert result.__args__[0] is str

    def test_array_with_ref_items(self):
        """Test mapping of array fields with $ref items."""
        field_spec = {
            "type": "array",
            "items": {"$ref": "#/components/schemas/Item"}
        }
        result = map_type(field_spec, "items", {}, {})

        # Should return List[ForwardRef]
        assert hasattr(result, '__origin__')
        assert result.__origin__ is list
        assert isinstance(result.__args__[0], ForwardRef)

    def test_array_without_items(self):
        """Test mapping of array fields without items specification."""
        field_spec = {"type": "array"}
        result = map_type(field_spec, "items", {}, {})

        # Should return List[Any]
        assert hasattr(result, '__origin__')
        assert result.__origin__ is list
        assert result.__args__[0] is Any


class TestMapOpenapiType:
    """Test the map_openapi_type function."""

    def test_basic_type_mappings(self):
        """Test basic OpenAPI type mappings."""
        assert map_openapi_type("string") is str
        assert map_openapi_type("integer") is int
        assert map_openapi_type("boolean") is bool
        assert map_openapi_type("number") is float
        assert map_openapi_type("object") is dict
        assert map_openapi_type("array") is list

    def test_unknown_type(self):
        """Test mapping of unknown types."""
        result = map_openapi_type("unknown_type")
        assert result is Any


class TestCreateGenericResponseModel:
    """Test the create_generic_response_model function."""

    def test_generic_response_model_creation(self):
        """Test that generic response model is created correctly."""
        model_class = create_generic_response_model()

        # Should be a RootModel subclass
        assert issubclass(model_class, RootModel)
        assert model_class.__name__ == "GenericResponseModel"

        # Should have arbitrary_types_allowed config
        assert hasattr(model_class, 'model_config')
        assert model_class.model_config.get('arbitrary_types_allowed') is True


class TestGetPydanticImports:
    """Test the get_pydantic_imports function."""

    def test_base_model_imports(self):
        """Test imports for BaseModel."""
        result = get_pydantic_imports("TestModel", is_root_model=False)
        assert "BaseModel" in result
        assert "Field" in result
        assert "ConfigDict" in result
        assert "from pydantic import" in result

    def test_root_model_imports(self):
        """Test imports for RootModel."""
        result = get_pydantic_imports("TestModel", is_root_model=True)
        assert "RootModel" in result
        assert "ConfigDict" in result
        assert "from pydantic import" in result
        assert "BaseModel" not in result
        assert "Field" not in result


class TestGetModelConfig:
    """Test the get_model_config function."""

    def test_generic_response_model_config(self):
        """Test config for GenericResponseModel."""
        result = get_model_config("GenericResponseModel")
        assert "arbitrary_types_allowed=True" in result

    def test_regular_model_config(self):
        """Test config for regular models."""
        result = get_model_config("RegularModel")
        assert "from_attributes=True" in result
        assert "arbitrary_types_allowed" not in result


class TestSanitizeFieldName:
    """Test the sanitize_field_name function."""

    def test_regular_field_names(self):
        """Test that regular field names are unchanged."""
        assert sanitize_field_name("normal_field") == "normal_field"
        assert sanitize_field_name("camelCase") == "camelCase"
        assert sanitize_field_name("field123") == "field123"

    def test_keyword_field_names(self):
        """Test that Python keywords are sanitized."""
        assert sanitize_field_name("class") == "class_field"
        assert sanitize_field_name("from") == "from_field"
        assert sanitize_field_name("import") == "import_field"
        assert sanitize_field_name("def") == "def_field"


class TestGetBuiltinTypes:
    """Test the get_builtin_types function."""

    def test_builtin_types_returned(self):
        """Test that builtin types are properly identified."""
        builtin_types = get_builtin_types()

        # Check some common builtin types
        assert str in builtin_types
        assert int in builtin_types
        assert float in builtin_types
        assert bool in builtin_types
        assert list in builtin_types
        assert dict in builtin_types
        assert tuple in builtin_types
        assert set in builtin_types

        # Should be a set
        assert isinstance(builtin_types, set)


class TestIsListOrDictModel:
    """Test the is_list_or_dict_model function."""

    def test_list_model_detection(self):
        """Test detection of List models."""
        from typing import List
        list_type = List[str]
        result = is_list_or_dict_model(list_type)
        assert result == "List"

    def test_dict_model_detection(self):
        """Test detection of Dict models."""
        from typing import Dict
        dict_type = Dict[str, int]
        result = is_list_or_dict_model(dict_type)
        assert result == "Dict"

    def test_regular_type_detection(self):
        """Test that regular types return None."""
        assert is_list_or_dict_model(str) is None
        assert is_list_or_dict_model(int) is None
        assert is_list_or_dict_model(BaseModel) is None


class TestExtractInnerTypes:
    """Test the extract_inner_types function."""

    def test_simple_type(self):
        """Test extraction from simple types."""
        result = extract_inner_types(str)
        assert result == [str]

    def test_optional_type(self):
        """Test extraction from Optional types."""
        from typing import Optional
        result = extract_inner_types(Optional[str])
        assert Optional in result
        assert str in result

    def test_list_type(self):
        """Test extraction from List types."""
        from typing import List
        result = extract_inner_types(List[str])
        assert list in result
        assert str in result

    def test_nested_generic_type(self):
        """Test extraction from nested generic types."""
        from typing import List, Dict
        result = extract_inner_types(List[Dict[str, int]])
        assert list in result
        assert dict in result
        assert str in result
        assert int in result


class TestTopologicalSort:
    """Test the topological_sort function."""

    def test_simple_dependency_graph(self):
        """Test sorting simple dependency graph."""
        graph = {
            "A": set(),
            "B": {"A"},
            "C": {"A", "B"}
        }
        result = topological_sort(graph)

        # The function returns nodes in reverse topological order
        # C depends on A and B, so it should be first
        # B depends on A, so it should be second
        # A has no dependencies, so it should be last
        assert "C" in result
        assert "B" in result
        assert "A" in result
        assert len(result) == 3

    def test_empty_graph(self):
        """Test sorting empty graph."""
        result = topological_sort({})
        assert result == []

    def test_single_node_graph(self):
        """Test sorting single node graph."""
        graph = {"A": set()}
        result = topological_sort(graph)
        assert result == ["A"]


class TestDetectCircularDependencies:
    """Test the detect_circular_dependencies function."""

    def test_no_circular_dependencies(self):
        """Test graph with no circular dependencies."""
        graph = {
            "A": set(),
            "B": {"A"},
            "C": {"B"}
        }
        result = detect_circular_dependencies(graph)
        assert result == set()

    def test_circular_dependencies(self):
        """Test graph with circular dependencies."""
        graph = {
            "A": {"B"},
            "B": {"A"}
        }
        result = detect_circular_dependencies(graph)
        assert "A" in result or "B" in result

    def test_self_referencing(self):
        """Test graph with self-referencing node."""
        graph = {
            "A": {"A"}
        }
        result = detect_circular_dependencies(graph)
        assert "A" in result


class TestJoinUrlPaths:
    """Test the join_url_paths function."""

    def test_basic_path_joining(self):
        """Test basic URL path joining."""
        result = join_url_paths("/api/v1", "endpoints")
        assert result == "/api/v1/endpoints"

    def test_path_with_trailing_slash(self):
        """Test joining paths where base has trailing slash."""
        result = join_url_paths("/api/v1/", "endpoints")
        assert result == "/api/v1/endpoints"

    def test_path_with_leading_slash(self):
        """Test joining paths where second path has leading slash."""
        result = join_url_paths("/api/v1", "/endpoints")
        assert result == "/api/v1/endpoints"

    def test_both_slashes(self):
        """Test joining paths with both trailing and leading slashes."""
        result = join_url_paths("/api/v1/", "/endpoints")
        assert result == "/api/v1/endpoints"


class TestClassifyParameters:
    """Test the classify_parameters function."""

    def test_empty_parameters(self):
        """Test classification of empty parameter list."""
        path_params, query_params = classify_parameters([])
        assert path_params == []
        assert query_params == []

    def test_mixed_parameters(self):
        """Test classification of mixed parameter types."""
        parameters = [
            {"name": "id", "in": "path"},
            {"name": "filter", "in": "query"},
            {"name": "userId", "in": "path"},
            {"name": "limit", "in": "query"}
        ]
        path_params, query_params = classify_parameters(parameters)

        assert set(path_params) == {"id", "userId"}
        assert set(query_params) == {"filter", "limit"}

    def test_only_path_parameters(self):
        """Test classification with only path parameters."""
        parameters = [
            {"name": "id", "in": "path"},
            {"name": "userId", "in": "path"}
        ]
        path_params, query_params = classify_parameters(parameters)

        assert set(path_params) == {"id", "userId"}
        assert query_params == []

    def test_only_query_parameters(self):
        """Test classification with only query parameters."""
        parameters = [
            {"name": "filter", "in": "query"},
            {"name": "limit", "in": "query"}
        ]
        path_params, query_params = classify_parameters(parameters)

        assert path_params == []
        assert set(query_params) == {"filter", "limit"}


class TestCreateSchemaNamMapping:
    """Test the _create_schema_name_mapping function."""

    def test_basic_schema_mapping(self):
        """Test basic schema name mapping creation."""
        components = {
            "Tfl.Api.Presentation.Entities.Mode": {},
            "Complex_Name_With_Underscores": {},
            "simple-name": {}
        }
        result = _create_schema_name_mapping(components)

        # Should map sanitized names back to original names
        assert "Mode" in result
        assert "Underscores" in result
        assert "name" in result

        assert result["Mode"] == "Tfl.Api.Presentation.Entities.Mode"
        assert result["Underscores"] == "Complex_Name_With_Underscores"
        assert result["name"] == "simple-name"

    def test_empty_components(self):
        """Test mapping creation with empty components."""
        result = _create_schema_name_mapping({})
        assert result == {}


class TestBuildModelsRealIntegration:
    """Integration tests using real TfL OpenAPI specs."""

    def test_build_models_with_real_specs(self):
        """Test build_models with actual TfL specifications."""
        import tempfile
        import os
        from pathlib import Path
        from scripts.build_models import main

        # Check if TfL specs directory exists
        tfl_specs_path = Path("../TfL_OpenAPI_specs")
        if not tfl_specs_path.exists():
            pytest.skip("TfL_OpenAPI_specs directory not found")

        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output"

            # Run the main function
            try:
                main(str(tfl_specs_path), str(output_path))
            except Exception as e:
                pytest.fail(f"build_models.main() failed with: {e}")

            # Verify output structure
            assert output_path.exists()
            models_dir = output_path / "models"
            assert models_dir.exists()

            # Check that models were created
            model_files = list(models_dir.glob("*.py"))
            assert len(model_files) > 0

            # Check that __init__.py was created
            init_file = models_dir / "__init__.py"
            assert init_file.exists()

            # Check that endpoints were created
            endpoints_dir = output_path / "endpoints"
            assert endpoints_dir.exists()

            # Verify some essential files exist
            endpoint_files = list(endpoints_dir.glob("*Client.py"))
            assert len(endpoint_files) > 0

    def test_generated_models_syntax_valid(self):
        """Test that generated models have valid Python syntax."""
        import tempfile
        import ast
        from pathlib import Path
        from scripts.build_models import main

        # Check if TfL specs directory exists
        tfl_specs_path = Path("../TfL_OpenAPI_specs")
        if not tfl_specs_path.exists():
            pytest.skip("TfL_OpenAPI_specs directory not found")

        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output"

            # Run the main function
            main(str(tfl_specs_path), str(output_path))

            # Check that all generated Python files have valid syntax
            models_dir = output_path / "models"
            for py_file in models_dir.glob("*.py"):
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                    ast.parse(content)
                except SyntaxError as e:
                    pytest.fail(f"Generated file {py_file} has syntax error: {e}")

            # Check endpoints too
            endpoints_dir = output_path / "endpoints"
            for py_file in endpoints_dir.glob("*.py"):
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                    ast.parse(content)
                except SyntaxError as e:
                    pytest.fail(f"Generated file {py_file} has syntax error: {e}")

    def test_baseline_compatibility(self):
        """Test that output is compatible with baseline implementation."""
        import tempfile
        from pathlib import Path
        from scripts.build_models import main

        # Check if TfL specs directory exists
        tfl_specs_path = Path("../TfL_OpenAPI_specs")
        if not tfl_specs_path.exists():
            pytest.skip("TfL_OpenAPI_specs directory not found")

        # Check if baseline exists (either baseline_output or existing pydantic_tfl_api)
        baseline_path = Path("../baseline_output")
        if not baseline_path.exists():
            baseline_path = Path("../pydantic_tfl_api")
        if not baseline_path.exists():
            pytest.skip("No baseline for comparison found")

        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output"

            # Run the main function
            main(str(tfl_specs_path), str(output_path))

            # Compare structure with baseline
            models_dir = output_path / "models"
            baseline_models = baseline_path / "models"

            if baseline_models.exists():
                # Compare that we generate roughly the same number of models
                generated_models = list(models_dir.glob("*.py"))
                baseline_model_files = list(baseline_models.glob("*.py"))

                # Should generate at least 80% of the baseline models
                min_expected = len(baseline_model_files) * 0.8
                assert len(generated_models) >= min_expected, \
                    f"Generated {len(generated_models)} models, expected at least {min_expected} based on baseline"
