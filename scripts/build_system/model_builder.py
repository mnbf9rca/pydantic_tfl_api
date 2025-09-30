"""ModelBuilder class for creating Pydantic models from OpenAPI schemas."""

import logging
from enum import Enum
from typing import Any, ForwardRef, cast

from pydantic import BaseModel, Field, RootModel, create_model

from .utilities import clean_enum_name, map_openapi_type, sanitize_field_name, sanitize_name


class ModelBuilder:
    """Handles the creation of Pydantic models from OpenAPI component schemas."""

    def __init__(self) -> None:
        """Initialize the ModelBuilder with an empty models dictionary."""
        self.models: dict[str, type[BaseModel] | type] = {}
        self.model_descriptions: dict[str, str] = {}  # Model-level descriptions from OpenAPI
        self.field_descriptions: dict[str, dict[str, str]] = {}  # Field-level descriptions per model
        self.logger = logging.getLogger(__name__)

    def sanitize_name(self, name: str, prefix: str = "Model") -> str:
        """Sanitize names using the shared utility function."""
        return sanitize_name(name, prefix)

    def sanitize_field_name(self, field_name: str) -> str:
        """Sanitize field names using the shared utility function."""
        return sanitize_field_name(field_name)

    def map_openapi_type(self, openapi_type: str) -> type | Any:
        """Map OpenAPI types to Python types using the shared utility function."""
        return map_openapi_type(openapi_type)

    def create_enum_class(self, enum_name: str, enum_values: list[Any]) -> type[Enum]:
        """Dynamically create a Pydantic Enum class for the given enum values."""
        # Create a dictionary with cleaned enum names as keys and the original values as values
        # Handle uniqueness by adding suffix for duplicates
        enum_dict = {}
        name_counts: dict[str, int] = {}

        for v in enum_values:
            cleaned_name = clean_enum_name(str(v))

            # Handle duplicate names by appending a counter
            if cleaned_name in enum_dict:
                name_counts[cleaned_name] = name_counts.get(cleaned_name, 1) + 1
                unique_name = f"{cleaned_name}_{name_counts[cleaned_name]}"
            else:
                unique_name = cleaned_name
                name_counts[cleaned_name] = 1

            enum_dict[unique_name] = v

        # Dynamically create the Enum class
        # The Enum() function returns a type[Enum], cast for type checker
        return cast(type[Enum], Enum(enum_name, enum_dict))

    def map_type(
        self,
        field_spec: dict[str, Any],
        field_name: str,
        components: dict[str, Any],
        models: dict[str, type[BaseModel]],
    ) -> Any:
        """Map OpenAPI field specification to Python type annotation."""
        if "$ref" in field_spec:
            # Handle references using ForwardRef for proper type resolution
            ref_name = self.sanitize_name(field_spec["$ref"].split("/")[-1])
            return ForwardRef(ref_name)

        openapi_type: str = field_spec.get("type", "Any")

        # Handle enums with mixed types
        if "enum" in field_spec:
            enum_values = field_spec["enum"]
            # Capitalize just the first letter of the field name, leave the rest as is
            cap_field_name = field_name[0].upper() + field_name[1:]
            enum_name = f"{cap_field_name}Enum"
            # Dynamically create an enum class and return it
            return self.create_enum_class(enum_name, enum_values)

        # Handle arrays
        if openapi_type == "array":
            # Ensure that 'items' exist for arrays, fallback to Any if missing
            items_spec = field_spec.get("items", {})
            if items_spec:
                inner_type = self.map_type(items_spec, field_name, components, models)
                # Return the list type annotation
                # Use type: ignore since inner_type is a runtime value used as a type parameter
                return list[inner_type]  # type: ignore[valid-type]
            else:
                self.logger.warning("'items' missing in array definition, using Any")
                return list[Any]

        # Map standard OpenAPI types to Python types
        return self.map_openapi_type(openapi_type)

    def create_pydantic_models(self, components: dict[str, Any]) -> None:
        """Create Pydantic models from OpenAPI component schemas."""
        # First pass: create object models
        for model_name, model_spec in components.items():
            sanitized_name = self.sanitize_name(model_name)  # Ensure the model name is valid

            # Extract model-level description from OpenAPI spec
            if "description" in model_spec:
                self.model_descriptions[sanitized_name] = model_spec["description"]

            if model_spec.get("type") == "object":
                if "properties" not in model_spec:
                    # Fallback if 'properties' is missing
                    # just create a List model which accepts any dict
                    self.models[sanitized_name] = dict[str, Any]
                    self.logger.warning(
                        f"Object model {sanitized_name} has no valid 'properties'. Using dict[str, Any]."
                    )
                    continue
                # Handle object models first
                fields: dict[str, Any] = {}
                field_descs: dict[str, str] = {}
                required_fields = model_spec.get("required", [])
                for field_name, field_spec in model_spec["properties"].items():
                    field_type = self.map_type(
                        field_spec, field_name, components, self.models
                    )  # Map the OpenAPI type to Python type
                    sanitized_field_name = self.sanitize_field_name(field_name)

                    # Extract field-level description
                    if "description" in field_spec:
                        field_descs[sanitized_field_name] = field_spec["description"]

                    if field_name in required_fields:
                        fields[sanitized_field_name] = (
                            field_type,
                            Field(..., alias=field_name),
                        )
                    else:
                        fields[sanitized_field_name] = (
                            field_type | None,
                            Field(None, alias=field_name),
                        )

                # Store field descriptions from OpenAPI spec as-is
                if field_descs:
                    self.field_descriptions[sanitized_name] = field_descs

                self.models[sanitized_name] = create_model(sanitized_name, **fields)
                self.logger.info(f"Created object model: {sanitized_name}")

        # Second pass: handle array models referencing the object models
        for model_name, model_spec in components.items():
            sanitized_name = self.sanitize_name(model_name)
            if model_spec.get("type") == "array":
                # Handle array models
                items_spec = model_spec.get("items")
                if "$ref" in items_spec:
                    # Handle reference in 'items'
                    ref_model_name = self.sanitize_name(items_spec["$ref"].split("/")[-1])
                    if ref_model_name not in self.models:
                        raise KeyError(
                            f"Referenced model '{ref_model_name}' not found while creating array '{sanitized_name}'"
                        )
                    # Get the referenced model and create a RootModel-based array class
                    ref_model = self.models[ref_model_name]
                    # Create a RootModel subclass for the array to ensure it's a proper class
                    # This is necessary for Python 3.13+ compatibility where type aliases
                    # don't have __bases__ attribute
                    # Use type: ignore since ref_model is a runtime value used as a type parameter
                    array_model = type(
                        sanitized_name,
                        (RootModel[list[ref_model]],),  # type: ignore[valid-type]
                        {"__module__": __name__},
                    )
                    self.models[sanitized_name] = array_model
                    self.logger.info(f"Created array model: {sanitized_name} -> RootModel[list[{ref_model_name}]]")
                else:
                    # Fallback if 'items' is missing or doesn't have a reference
                    # Also use RootModel for consistency
                    array_model = type(sanitized_name, (RootModel[list[Any]],), {"__module__": __name__})
                    self.models[sanitized_name] = array_model
                    self.logger.warning(
                        f"Array model {sanitized_name} has no valid 'items' reference. Using RootModel[list[Any]]."
                    )

    def get_models(self) -> dict[str, type[BaseModel] | type]:
        """Return a copy of the models dictionary."""
        return self.models.copy()

    def get_model_descriptions(self) -> dict[str, str]:
        """Return a copy of the model descriptions dictionary."""
        return self.model_descriptions.copy()

    def get_field_descriptions(self) -> dict[str, dict[str, str]]:
        """Return a copy of the field descriptions dictionary."""
        return self.field_descriptions.copy()

    def clear_models(self) -> None:
        """Clear the models dictionary and descriptions."""
        self.models.clear()
        self.model_descriptions.clear()
        self.field_descriptions.clear()
