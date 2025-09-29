"""ModelBuilder class for creating Pydantic models from OpenAPI schemas."""

import logging
from enum import Enum
from typing import Any, ForwardRef

from pydantic import BaseModel, Field, create_model

from .utilities import map_openapi_type, sanitize_field_name, sanitize_name


class ModelBuilder:
    """Handles the creation of Pydantic models from OpenAPI component schemas."""

    def __init__(self) -> None:
        """Initialize the ModelBuilder with an empty models dictionary."""
        self.models: dict[str, type[BaseModel] | type] = {}
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
        from typing import cast

        from .utilities import clean_enum_name

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
                required_fields = model_spec.get("required", [])
                for field_name, field_spec in model_spec["properties"].items():
                    field_type = self.map_type(
                        field_spec, field_name, components, self.models
                    )  # Map the OpenAPI type to Python type
                    sanitized_field_name = self.sanitize_field_name(field_name)
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
                    # Get the referenced model and create a list type
                    ref_model = self.models[ref_model_name]
                    self.models[sanitized_name] = list[ref_model]  # type: ignore[valid-type]
                    self.logger.info(f"Created array model: {sanitized_name} -> list[{ref_model_name}]")
                else:
                    # Fallback if 'items' is missing or doesn't have a reference
                    self.models[sanitized_name] = list[Any]
                    self.logger.warning(
                        f"Array model {sanitized_name} has no valid 'items' reference. Using list[Any]."
                    )

        # Generate additional array models that are needed but not explicitly defined
        self.generate_additional_array_models()

    def generate_additional_array_models(self) -> None:
        """Generate additional RootModel-based array models for common types.

        Some models need array versions even if not explicitly defined in OpenAPI specs.
        This generates RootModel classes for these models based on production requirements.
        """
        from pydantic import ConfigDict, RootModel, create_model

        # Models that need array versions based on production system analysis
        # Format: (base_model_name, desired_array_name) or just base_model_name
        models_needing_arrays = [
            "ArrivalDeparture",
            "BikePointOccupancy",
            "ChargeConnectorOccupancy",
            "DisruptedPoint",
            "LineServiceType",
            # Note: PlaceCategory already has PlaceCategoryArray, and StopPointCategory
            # is deduplicated to PlaceCategory, so no need for StopPointCategoryArray
            "StopPointRouteSection",
        ]

        for model_config in models_needing_arrays:
            if isinstance(model_config, tuple):
                base_model_name, array_model_name = model_config
            else:
                base_model_name = model_config
                array_model_name = f"{base_model_name}Array"

            if base_model_name in self.models:
                # Only create if not already exists
                if array_model_name not in self.models:
                    base_model = self.models[base_model_name]

                    # Create RootModel-based array class
                    # Use type: ignore since base_model is a runtime value used as a type
                    array_class = create_model(
                        array_model_name,
                        __base__=RootModel[list[base_model]],  # type: ignore[valid-type]
                        __config__=ConfigDict(from_attributes=True),
                    )

                    self.models[array_model_name] = array_class
                    self.logger.info(f"Generated additional array model: {array_model_name} (from {base_model_name})")
                else:
                    self.logger.debug(f"Array model {array_model_name} already exists")
            else:
                self.logger.warning(f"Base model {base_model_name} not found for array generation")

    def get_models(self) -> dict[str, type[BaseModel] | type]:
        """Return a copy of the models dictionary."""
        return self.models.copy()

    def clear_models(self) -> None:
        """Clear the models dictionary."""
        self.models.clear()
