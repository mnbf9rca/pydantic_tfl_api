"""Tests for the refactored helper functions in build_models.py

These tests cover the new smaller functions that were extracted during refactoring.
"""

from io import StringIO

import pytest
from pydantic import BaseModel

from scripts.build_models import (
    collect_type_imports,
    create_method_docstring,
    create_method_implementation,
    create_method_signature,
    # API metadata functions
    extract_api_metadata,
    extract_list_dict_types,
    generate_import_lines,
    generate_list_dict_class_definition,
    validate_list_dict_args,
    write_imports_and_class,
)


class TestExtractApiMetadata:
    """Test API metadata extraction from OpenAPI specs."""

    def test_basic_metadata_extraction(self):
        """Test extracting basic metadata from OpenAPI spec."""
        spec = {
            "info": {"title": "Test API"},
            "paths": {"/test": {"get": {"operationId": "getTest"}}},
            "servers": [{"url": "https://api.example.com/v1/test"}]
        }

        class_name, api_path, paths = extract_api_metadata(spec)

        assert class_name == "TestApiClient"  # sanitize_name converts to camelCase
        assert api_path == "/v1/test"  # Extracts everything after the 3rd slash
        assert paths == {"/test": {"get": {"operationId": "getTest"}}}

    def test_missing_servers(self):
        """Test handling when servers section is missing."""
        spec = {
            "info": {"title": "Test API"},
            "paths": {"/test": {}},
            "servers": [{"url": "https://api.example.com/v1/test/api"}]  # Provide enough path segments
        }

        class_name, api_path, paths = extract_api_metadata(spec)

        assert class_name == "TestApiClient"
        assert api_path == "/v1/test/api"  # Extracts everything after the 3rd slash
        assert paths == {"/test": {}}


class TestCreateMethodSignature:
    """Test method signature creation."""

    def test_method_with_parameters(self):
        """Test creating method signature with parameters."""
        parameters = [
            {"name": "id", "schema": {"type": "string"}},
            {"name": "limit", "schema": {"type": "integer"}}
        ]

        signature = create_method_signature("getItems", parameters, "ItemList")

        assert "def getItems(self, id: str | None = None, limit: int | None = None)" in signature
        assert "-> ResponseModel[ItemList] | ApiError:" in signature

    def test_method_without_parameters(self):
        """Test creating method signature without parameters."""
        signature = create_method_signature("getAll", [], "ItemList")

        assert "def getAll(self, )" in signature
        assert "-> ResponseModel[ItemList] | ApiError:" in signature


class TestCreateMethodDocstring:
    """Test method docstring creation."""

    def test_docstring_with_parameters(self):
        """Test creating docstring with parameters."""
        details = {"description": "Get items by ID"}
        parameters = [
            {"name": "item_id", "schema": {"type": "string"}, "description": "Unique identifier"}
        ]

        docstring = create_method_docstring(details, "/api/items", "ItemList", parameters)

        assert "Get items by ID" in docstring
        assert "Query path: `/api/items`" in docstring
        assert "`ResponseModel.content` contains `models.ItemList` type" in docstring
        assert "`item_id`: str - Unique identifier" in docstring

    def test_docstring_without_parameters(self):
        """Test creating docstring without parameters."""
        details = {"description": "Get all items"}

        docstring = create_method_docstring(details, "/api/items", "ItemList", [])

        assert "Get all items" in docstring
        assert "No parameters required" in docstring


class TestCreateMethodImplementation:
    """Test method implementation creation."""

    def test_implementation_with_path_params(self):
        """Test creating implementation with path parameters."""
        parameters = [
            {"name": "id", "in": "path", "schema": {"type": "string"}},
            {"name": "limit", "in": "query", "schema": {"type": "integer"}}
        ]

        implementation = create_method_implementation("getItem", parameters)

        assert "params=[id]" in implementation
        assert "endpoint_args={ 'limit': limit }" in implementation

    def test_implementation_query_only(self):
        """Test creating implementation with only query parameters."""
        parameters = [
            {"name": "limit", "in": "query", "schema": {"type": "integer"}}
        ]

        implementation = create_method_implementation("getItems", parameters)

        assert "params=" not in implementation or "params=[]" in implementation
        assert "endpoint_args={ 'limit': limit }" in implementation

    def test_implementation_no_params(self):
        """Test creating implementation without parameters."""
        implementation = create_method_implementation("getAll", [])

        assert "endpoint_args=None" in implementation


class TestGenerateImportLines:
    """Test import line generation."""

    def test_basic_imports(self):
        """Test generating basic import lines."""
        all_types = {str, int}
        all_package_models = {"Item", "User"}

        import_lines = generate_import_lines("TestClient", all_types, all_package_models)

        import_text = "".join(import_lines)
        assert "from .TestClient_config import endpoints, base_url" in import_text
        assert "from ..core import ApiError, ResponseModel, Client" in import_text
        assert "from ..models import Item, User" in import_text

    def test_no_package_models(self):
        """Test generating imports without package models."""
        import_lines = generate_import_lines("TestClient", set(), set())

        import_text = "".join(import_lines)
        assert "from .TestClient_config import endpoints, base_url" in import_text
        assert "from ..core import ApiError, ResponseModel, Client" in import_text
        assert "from ..models import" not in import_text


class TestValidateListDictArgs:
    """Test list/dict argument validation."""

    def test_valid_list_args(self):
        """Test validation passes for valid list arguments."""
        # Should not raise any exception
        validate_list_dict_args("list", (str,))

    def test_valid_dict_args(self):
        """Test validation passes for valid dict arguments."""
        # Should not raise any exception
        validate_list_dict_args("dict", (str, int))

    def test_invalid_list_args(self):
        """Test validation fails for invalid list arguments."""
        with pytest.raises(ValueError, match="list type should have exactly 1 argument, got 2"):
            validate_list_dict_args("list", (str, int))

    def test_invalid_dict_args(self):
        """Test validation fails for invalid dict arguments."""
        with pytest.raises(ValueError, match="dict type should have exactly 2 arguments"):
            validate_list_dict_args("dict", (str,))


class TestExtractListDictTypes:
    """Test type extraction from list/dict arguments."""

    def test_extract_list_types(self):
        """Test extracting types from list arguments."""
        inner_type, key_type, value_type = extract_list_dict_types("list", (str,))

        assert inner_type == str
        assert key_type is None
        assert value_type == str

    def test_extract_dict_types(self):
        """Test extracting types from dict arguments."""
        inner_type, key_type, value_type = extract_list_dict_types("dict", (str, int))

        assert inner_type == int  # For backward compatibility
        assert key_type == str
        assert value_type == int

    def test_unsupported_model_type(self):
        """Test error for unsupported model types."""
        with pytest.raises(ValueError, match="Unsupported model type: tuple"):
            extract_list_dict_types("tuple", (str, int))


class TestCollectTypeImports:
    """Test type import collection."""

    def test_builtin_type_import(self):
        """Test that builtin types don't generate imports."""
        typing_imports = set()
        module_imports = set()
        models = {}

        type_name = collect_type_imports(str, models, typing_imports, module_imports)

        assert type_name == "str"
        assert len(typing_imports) == 0
        assert len(module_imports) == 0

    def test_model_type_import(self):
        """Test that model types generate module imports."""
        typing_imports = set()
        module_imports = set()

        class TestModel(BaseModel):
            pass

        models = {"TestModel": TestModel}

        type_name = collect_type_imports(TestModel, models, typing_imports, module_imports)

        assert type_name == "TestModel"
        assert "from .TestModel import TestModel" in module_imports

    def test_unknown_type_import(self):
        """Test handling of unknown types."""
        typing_imports = set()
        module_imports = set()
        models = {}

        # Create a mock type object
        class MockType:
            pass

        mock_type = MockType()
        type_name = collect_type_imports(mock_type, models, typing_imports, module_imports)

        assert type_name == "Any"


class TestGenerateListDictClassDefinition:
    """Test class definition generation for list/dict models."""

    def test_list_class_definition(self):
        """Test generating class definition for list models."""
        type_names = {"inner": "str"}

        class_def = generate_list_dict_class_definition("list", "StringArray", type_names)

        assert class_def == "class StringArray(RootModel[list[str]]):\n"

    def test_dict_class_definition(self):
        """Test generating class definition for dict models."""
        type_names = {"key": "str", "value": "int"}

        class_def = generate_list_dict_class_definition("dict", "StringIntDict", type_names)

        assert class_def == "class StringIntDict(RootModel[dict[str, int]]):\n"

    def test_invalid_model_type(self):
        """Test error for invalid model types."""
        with pytest.raises(ValueError, match="Model is not a list or dict model"):
            generate_list_dict_class_definition("tuple", "TestClass", {})


class TestWriteImportsAndClass:
    """Test writing imports and class to file."""

    def test_write_complete_class(self):
        """Test writing complete class with imports."""
        model_file = StringIO()
        typing_imports = {"Optional"}
        module_imports = {"from .TestModel import TestModel"}
        class_definition = "class TestArray(RootModel[list[TestModel]]):\n"

        write_imports_and_class(model_file, typing_imports, module_imports,
                               class_definition, "TestArray")

        content = model_file.getvalue()
        assert "from typing import Optional" in content
        assert "from .TestModel import TestModel" in content
        assert "class TestArray(RootModel[list[TestModel]]):" in content
        assert "model_config = ConfigDict(from_attributes=True)" in content

    def test_write_class_no_imports(self):
        """Test writing class without imports."""
        model_file = StringIO()
        class_definition = "class SimpleArray(RootModel[list[str]]):\n"

        write_imports_and_class(model_file, set(), set(), class_definition, "SimpleArray")

        content = model_file.getvalue()
        assert "from typing import" not in content
        assert "class SimpleArray(RootModel[list[str]]):" in content
        assert "model_config = ConfigDict(from_attributes=True)" in content
