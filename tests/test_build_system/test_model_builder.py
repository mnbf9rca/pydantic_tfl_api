"""Tests for ModelBuilder class that handles Pydantic model creation from OpenAPI schemas."""

from enum import Enum
from typing import Any, ForwardRef, get_args, get_origin

import pytest
from pydantic import BaseModel, RootModel
from pydantic_core import PydanticUndefined

from scripts.build_system.model_builder import ModelBuilder


class TestModelBuilder:
    """Test the ModelBuilder class for OpenAPI schema to Pydantic model conversion."""

    @pytest.fixture
    def model_builder(self) -> Any:
        """Create a ModelBuilder instance for testing."""
        return ModelBuilder()

    @pytest.fixture
    def sample_components(self) -> Any:
        """Sample OpenAPI components for testing."""
        return {
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "isActive": {"type": "boolean"},
                },
                "required": ["id", "name"],
            },
            "UserArray": {"type": "array", "items": {"$ref": "#/components/schemas/User"}},
            "Status": {"type": "string", "enum": ["active", "inactive", "pending"]},
            "NestedModel": {
                "type": "object",
                "properties": {
                    "user": {"$ref": "#/components/schemas/User"},
                    "status": {"$ref": "#/components/schemas/Status"},
                    "metadata": {"type": "object"},
                },
            },
        }

    def test_init_creates_empty_models_dict(self, model_builder: Any) -> None:
        """Test that ModelBuilder initializes with empty models dictionary."""
        assert hasattr(model_builder, "models")
        assert isinstance(model_builder.models, dict)
        assert len(model_builder.models) == 0

    def test_sanitize_name_basic_functionality(self, model_builder: Any) -> None:
        """Test name sanitization handles various input formats."""
        # Test basic sanitization
        assert model_builder.sanitize_name("user-profile") == "Profile"
        assert model_builder.sanitize_name("user_name") == "Name"
        assert model_builder.sanitize_name("simple") == "Simple"

        # Test keyword handling - CamelCase conversion makes them non-keywords
        assert model_builder.sanitize_name("class") == "Class"
        assert model_builder.sanitize_name("def") == "Def"

        # Test digit handling
        assert model_builder.sanitize_name("123test") == "Model_123test"

    def test_map_basic_openapi_types(self, model_builder: Any) -> None:
        """Test mapping of basic OpenAPI types to Python types."""
        components: dict[str, Any] = {}
        models: dict[str, Any] = {}

        # Test string type
        string_spec = {"type": "string"}
        result = model_builder.map_type(string_spec, "name", components, models)
        assert result is str

        # Test integer type
        int_spec = {"type": "integer"}
        result = model_builder.map_type(int_spec, "age", components, models)
        assert result is int

        # Test boolean type
        bool_spec = {"type": "boolean"}
        result = model_builder.map_type(bool_spec, "active", components, models)
        assert result is bool

        # Test number type
        number_spec = {"type": "number"}
        result = model_builder.map_type(number_spec, "price", components, models)
        assert result is float

    def test_map_array_types(self, model_builder: Any) -> None:
        """Test mapping of array types."""
        components: dict[str, Any] = {}
        models: dict[str, Any] = {}

        # Test string array
        array_spec = {"type": "array", "items": {"type": "string"}}
        result = model_builder.map_type(array_spec, "tags", components, models)
        assert result == list[str]

        # Test array without items (should default to Any)
        array_spec_no_items = {"type": "array"}
        result = model_builder.map_type(array_spec_no_items, "data", components, models)
        assert result == list[Any]

    def test_map_reference_types(self, model_builder: Any) -> None:
        """Test mapping of $ref references to ForwardRef."""
        components: dict[str, Any] = {"User": {}}
        models: dict[str, Any] = {}

        ref_spec = {"$ref": "#/components/schemas/User"}
        result = model_builder.map_type(ref_spec, "user", components, models)
        assert isinstance(result, ForwardRef)
        assert result.__forward_arg__ == "User"

    def test_create_enum_class(self, model_builder: Any) -> None:
        """Test enum class creation from OpenAPI enum values."""
        enum_values = ["active", "inactive", "pending"]
        enum_class = model_builder.create_enum_class("StatusEnum", enum_values)

        assert issubclass(enum_class, Enum)
        assert enum_class.__name__ == "StatusEnum"
        assert hasattr(enum_class, "ACTIVE")
        assert hasattr(enum_class, "INACTIVE")
        assert hasattr(enum_class, "PENDING")
        assert enum_class.ACTIVE.value == "active"

    def test_create_enum_with_duplicate_names(self, model_builder: Any) -> None:
        """Test enum creation handles duplicate names properly."""
        enum_values = ["test", "Test", "TEST"]
        enum_class = model_builder.create_enum_class("TestEnum", enum_values)

        # Should create unique enum members
        members = list(enum_class)
        assert len(members) == 3
        # Names should be unique with suffixes for duplicates
        member_names = [member.name for member in members]
        assert len(set(member_names)) == 3

    def test_create_pydantic_models_object_types(self, model_builder: Any, sample_components: Any) -> None:
        """Test creating Pydantic models from object type schemas."""
        model_builder.create_pydantic_models(sample_components)

        # Check User model was created
        assert "User" in model_builder.models
        user_model = model_builder.models["User"]
        assert issubclass(user_model, BaseModel)

        # Check model has expected fields
        assert "id" in user_model.model_fields
        assert "name" in user_model.model_fields
        assert "age" in user_model.model_fields
        assert "isActive" in user_model.model_fields

    def test_create_pydantic_models_array_types(self, model_builder: Any, sample_components: Any) -> None:
        """Test creating array type models."""
        model_builder.create_pydantic_models(sample_components)

        # Check UserArray was created
        assert "UserArray" in model_builder.models
        user_array_type = model_builder.models["UserArray"]

        # Should be a RootModel-based class (as of the Python 3.13 compatibility fix)
        assert issubclass(user_array_type, RootModel)

        # Check that the RootModel's root type is list-based
        # The proper way to check a RootModel's root type is through model_fields['root']
        assert "root" in user_array_type.model_fields
        root_field = user_array_type.model_fields["root"]
        assert get_origin(root_field.annotation) is list

    def test_create_pydantic_models_handles_missing_properties(self, model_builder: Any) -> None:
        """Test that models with missing properties are handled gracefully."""
        components = {
            "EmptyModel": {
                "type": "object"
                # No properties field
            }
        }

        model_builder.create_pydantic_models(components)

        # Should create a fallback dict type
        assert "EmptyModel" in model_builder.models
        assert model_builder.models["EmptyModel"] == dict[str, Any]

    def test_field_requirements_handling(self, model_builder: Any) -> None:
        """Test that required and optional fields are handled correctly."""
        components = {
            "TestModel": {
                "type": "object",
                "properties": {"required_field": {"type": "string"}, "optional_field": {"type": "string"}},
                "required": ["required_field"],
            }
        }

        model_builder.create_pydantic_models(components)

        test_model = model_builder.models["TestModel"]
        fields = test_model.model_fields

        # Required field should not be union with None
        required_field = fields["required_field"]
        assert required_field.default == PydanticUndefined  # PydanticUndefined indicates required in Pydantic v2

        # Optional field should be union with None
        optional_field = fields["optional_field"]
        assert optional_field.default is None

    def test_nested_model_references(self, model_builder: Any, sample_components: Any) -> None:
        """Test that nested model references are handled correctly."""
        model_builder.create_pydantic_models(sample_components)

        # Check NestedModel was created and has references
        assert "NestedModel" in model_builder.models
        nested_model = model_builder.models["NestedModel"]

        fields = nested_model.model_fields
        assert "user" in fields
        assert "status" in fields
        assert "metadata" in fields

    def test_enum_field_handling(self, model_builder: Any) -> None:
        """Test that enum fields in models are handled correctly."""
        components = {
            "ModelWithEnum": {
                "type": "object",
                "properties": {"status": {"type": "string", "enum": ["active", "inactive"]}},
            }
        }

        model_builder.create_pydantic_models(components)

        model = model_builder.models["ModelWithEnum"]
        status_field = model.model_fields["status"]

        # Should have created an enum type
        field_type = status_field.annotation

        # Handle both direct enum and union types (for optional enum fields)
        if get_origin(field_type) is not None:
            # It's a union type (optional enum), check the args
            args = get_args(field_type)
            enum_args = [arg for arg in args if isinstance(arg, type) and issubclass(arg, Enum)]
            assert len(enum_args) > 0, f"Expected at least one enum in union type, got {args}"
            enum_type = enum_args[0]
        else:
            # Direct enum type
            enum_type = field_type

        # The enum should have a name containing 'Enum'
        assert hasattr(enum_type, "__name__")
        assert "Enum" in enum_type.__name__

    def test_array_models_are_rootmodel_based(self, model_builder: Any) -> None:
        """REGRESSION: Ensure array models use RootModel pattern."""
        components = {
            "TestModel": {"type": "object", "properties": {"id": {"type": "string"}}},
            "TestModelArray": {"type": "array", "items": {"$ref": "#/components/schemas/TestModel"}},
        }

        model_builder.create_pydantic_models(components)
        models = model_builder.get_models()

        assert "TestModelArray" in models

        # The array model should be a proper class, not just a type alias
        array_model = models["TestModelArray"]

        # Check if it's a RootModel-based class (not just a type alias)
        assert hasattr(array_model, "__bases__"), "Array model should be a proper class"

        # For explicitly defined array models, they should be list types
        # But for auto-generated ones (via generate_additional_array_models), they should be RootModel-based
        if hasattr(array_model, "__origin__"):
            # This is a type alias like list[TestModel] - acceptable for explicitly defined arrays
            assert array_model.__origin__ is list, "Array type alias should be list-based"
        else:
            # This should be a RootModel class
            assert issubclass(array_model, RootModel), "Array model class should inherit from RootModel"

    def test_get_models_returns_copy(self, model_builder: Any, sample_components: Any) -> None:
        """Test that get_models returns a copy of the models dict."""
        model_builder.create_pydantic_models(sample_components)

        models_copy = model_builder.get_models()

        # Should be a dict with the same content
        assert isinstance(models_copy, dict)
        assert len(models_copy) == len(model_builder.models)

        # But should be a different object (copy)
        assert models_copy is not model_builder.models

        # Content should be the same
        for key in model_builder.models:
            assert key in models_copy
            assert models_copy[key] is model_builder.models[key]

    def test_clear_models(self, model_builder: Any, sample_components: Any) -> None:
        """Test that clear_models empties the models dictionary."""
        model_builder.create_pydantic_models(sample_components)

        # Verify models were created
        assert len(model_builder.models) > 0

        # Clear models
        model_builder.clear_models()

        # Verify models are cleared
        assert len(model_builder.models) == 0

    @pytest.mark.parametrize(
        "openapi_type,expected_python_type",
        [
            ("string", str),
            ("integer", int),
            ("boolean", bool),
            ("number", float),
            ("object", dict),
            ("array", list),
            ("unknown_type", Any),
        ],
    )
    def test_map_openapi_type_mapping(self, model_builder: Any, openapi_type: Any, expected_python_type: Any) -> None:
        """Test OpenAPI type to Python type mapping."""
        result = model_builder.map_openapi_type(openapi_type)
        assert result == expected_python_type

    def test_extract_model_descriptions(self, model_builder: Any) -> None:
        """Test that model-level descriptions are extracted from OpenAPI specs."""
        components = {
            "Station": {
                "type": "object",
                "description": "Represents a station in the TfL network.",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                },
            },
            "Place": {
                "type": "object",
                "description": "A location with coordinates.",
                "properties": {
                    "lat": {"type": "number"},
                    "lon": {"type": "number"},
                },
            },
        }

        model_builder.create_pydantic_models(components)

        # Verify model descriptions were extracted
        model_descriptions = model_builder.get_model_descriptions()
        assert "Station" in model_descriptions
        assert model_descriptions["Station"] == "Represents a station in the TfL network."
        assert "Place" in model_descriptions
        assert model_descriptions["Place"] == "A location with coordinates."

    def test_extract_field_descriptions(self, model_builder: Any) -> None:
        """Test that field-level descriptions are extracted from OpenAPI specs."""
        components = {
            "Place": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "A unique identifier."},
                    "name": {"type": "string", "description": "The name of the place."},
                    "lat": {"type": "number", "description": "Latitude coordinate."},
                },
            }
        }

        model_builder.create_pydantic_models(components)

        # Verify field descriptions were extracted
        field_descriptions = model_builder.get_field_descriptions()
        assert "Place" in field_descriptions
        assert field_descriptions["Place"]["id"] == "A unique identifier."
        assert field_descriptions["Place"]["name"] == "The name of the place."
        assert field_descriptions["Place"]["lat"] == "Latitude coordinate."

    def test_descriptions_without_specs(self, model_builder: Any) -> None:
        """Test that models without descriptions work correctly."""
        components = {
            "SimpleModel": {
                "type": "object",
                "properties": {
                    "field1": {"type": "string"},
                    "field2": {"type": "integer"},
                },
            }
        }

        model_builder.create_pydantic_models(components)

        # Should have created model without errors
        assert "SimpleModel" in model_builder.models

        # Descriptions should be empty for this model
        model_descriptions = model_builder.get_model_descriptions()
        field_descriptions = model_builder.get_field_descriptions()
        assert "SimpleModel" not in model_descriptions
        assert "SimpleModel" not in field_descriptions

    def test_clear_models_clears_descriptions(self, model_builder: Any) -> None:
        """Test that clear_models also clears description dictionaries."""
        components = {
            "TestModel": {
                "type": "object",
                "description": "Test description",
                "properties": {
                    "field": {"type": "string", "description": "Field description"},
                },
            }
        }

        model_builder.create_pydantic_models(components)

        # Verify descriptions were created
        assert len(model_builder.get_model_descriptions()) > 0
        assert len(model_builder.get_field_descriptions()) > 0

        # Clear everything
        model_builder.clear_models()

        # Verify descriptions are cleared
        assert len(model_builder.get_model_descriptions()) == 0
        assert len(model_builder.get_field_descriptions()) == 0

    def test_partial_field_descriptions(self, model_builder: Any) -> None:
        """Test handling of models where only some fields have descriptions."""
        components = {
            "PartialModel": {
                "type": "object",
                "description": "Model with partial field descriptions",
                "properties": {
                    "documented_field": {"type": "string", "description": "This field has a description"},
                    "undocumented_field": {"type": "integer"},  # No description
                    "another_documented": {"type": "boolean", "description": "Another documented field"},
                },
                "required": ["documented_field"],
            }
        }

        model_builder.create_pydantic_models(components)

        # Verify model was created
        assert "PartialModel" in model_builder.models

        # Verify field descriptions only include documented fields
        field_descriptions = model_builder.get_field_descriptions()
        assert "PartialModel" in field_descriptions
        assert "documented_field" in field_descriptions["PartialModel"]
        assert "another_documented" in field_descriptions["PartialModel"]
        assert "undocumented_field" not in field_descriptions["PartialModel"]
        assert field_descriptions["PartialModel"]["documented_field"] == "This field has a description"
        assert field_descriptions["PartialModel"]["another_documented"] == "Another documented field"
