"""Shared utility functions for the build system."""

import builtins
import json
import keyword
import logging
import re
import types
from typing import Any, Optional, Union, get_args, get_origin
from urllib.parse import urljoin

from pydantic import BaseModel, RootModel


def sanitize_name(name: str, prefix: str = "Model") -> str:
    """
    Sanitize class names or field names to ensure they are valid Python identifiers.

    1. Replace invalid characters (like hyphens) with underscores.
    2. Extract the portion after the last underscore for more concise names.
    3. Prepend prefix only if the final result would be invalid.

    Args:
        name: The name to sanitize
        prefix: Prefix to use if name is invalid

    Returns:
        Sanitized name that is a valid Python identifier
    """
    # Replace invalid characters (like hyphens) with underscores, preserve spaces temporarily
    sanitized = re.sub(r"[^a-zA-Z0-9_ ]", "_", name)

    # Convert spaces to CamelCase first
    words = sanitized.split()
    if len(words) > 1:
        # Convert multiple words to CamelCase ("Lift Disruptions" -> "LiftDisruptions")
        sanitized = "".join(word.capitalize() for word in words)
    elif words:
        sanitized = words[0]

    # Extract the portion after the last underscore for concise names
    if "_" in sanitized:
        sanitized = sanitized.split("_")[-1]

    # Convert to CamelCase if it's all lowercase
    if sanitized and sanitized.islower():
        sanitized = sanitized.capitalize()

    # Prepend prefix only if the final result would be invalid
    if sanitized and (sanitized[0].isdigit() or keyword.iskeyword(sanitized)):
        sanitized = f"{prefix}_{sanitized}"

    return sanitized


def sanitize_field_name(field_name: str) -> str:
    """Sanitize field names that are Python reserved keywords."""
    return f"{field_name}_field" if keyword.iskeyword(field_name) else field_name


def get_builtin_types() -> set:
    """Return a set of all built-in Python types."""
    return {obj for name, obj in vars(builtins).items() if isinstance(obj, type)}


def map_openapi_type(openapi_type: str) -> type | Any:
    """Map OpenAPI types to Python types."""
    return {
        "string": str,
        "integer": int,
        "boolean": bool,
        "number": float,
        "object": dict,
        "array": list,
    }.get(openapi_type, Any)


def extract_inner_types(annotation: Any) -> list[Any]:
    """Recursively extract and preserve inner types from nested generics, returning actual type objects."""
    origin = get_origin(annotation)

    # Handle modern union syntax (Python 3.10+): X | Y creates types.UnionType
    if isinstance(origin, types.UnionType) or origin is types.UnionType:
        args = get_args(annotation)
        non_none_args = []
        contains_none = False
        for arg in args:
            if arg is type(None):
                contains_none = True
            else:
                non_none_args.extend(extract_inner_types(arg))  # Accumulate all inner types
        # Return types.UnionType as the origin for modern union syntax
        return [types.UnionType] + non_none_args

    # Handle classic Union syntax (typing.Union)
    if origin is Union:
        args = get_args(annotation)
        non_none_args = []
        contains_none = False
        for arg in args:
            if arg is type(None):
                contains_none = True
            else:
                non_none_args.extend(extract_inner_types(arg))  # Accumulate all inner types
        if contains_none:  # If NoneType was present, it's Optional
            return [Union] + non_none_args
        else:
            return [Union] + non_none_args

    # If it's a generic type (e.g., List, Dict), recurse into its arguments
    elif origin:
        inner_types = []
        for arg in get_args(annotation):
            inner_types.extend(extract_inner_types(arg))  # Accumulate inner types recursively
        return [origin] + inner_types  # Return the actual origin (e.g., List, Dict) instead of its name

    # Base case: return the actual class/type
    return [annotation]


def clean_enum_name(value: str) -> str:
    """Clean enum names by replacing special characters and making uppercase."""
    # Replace special characters with underscores
    cleaned = re.sub(r"\W", "_", value).replace("-", "_")

    # Add underscore prefix if starts with a digit
    if cleaned and cleaned[0].isdigit():
        cleaned = "_" + cleaned

    # Remove trailing underscores (but keep leading underscore if it was added above)
    cleaned = cleaned.rstrip("_")

    return cleaned.upper()


def join_url_paths(a: str, b: str) -> str:
    """Join URL paths ensuring proper slash handling."""
    # Ensure the base path ends with a slash for urljoin to work properly
    return urljoin(a + "/", b.lstrip("/"))


def are_models_equal(model1: Any, model2: Any) -> bool:
    """Check if two Pydantic models are equal based on their fields, types, and metadata.

    Args:
        model1: First model to compare
        model2: Second model to compare

    Returns:
        True if models are equal, False otherwise
    """
    # Must both be BaseModel types
    if not (isinstance(model1, type) and isinstance(model2, type)):
        return False
    if not (issubclass(model1, BaseModel) and issubclass(model2, BaseModel)):
        return False

    # Compare field structure
    if set(model1.model_fields.keys()) != set(model2.model_fields.keys()):
        return False

    # Compare each field's annotation, alias, default, and constraints
    for field_name in model1.model_fields:
        field1 = model1.model_fields[field_name]
        field2 = model2.model_fields[field_name]

        # Compare field annotations
        if str(field1.annotation) != str(field2.annotation):
            return False

        # Compare aliases
        if field1.alias != field2.alias:
            return False

        # Compare default values
        if field1.default != field2.default:
            return False

        # Compare if field is required
        if field1.is_required() != field2.is_required():
            return False

        # Compare field constraints (title, description, etc.)
        if (
            hasattr(field1, "json_schema_extra")
            and hasattr(field2, "json_schema_extra")
            and field1.json_schema_extra != field2.json_schema_extra
        ):
            return False

    return True


def deduplicate_models(
    models: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, str]]:
    """Deduplicate models by removing models with the same content.

    Args:
        models: Dictionary of model names to model classes

    Returns:
        Tuple of (deduplicated_models, reference_map) where reference_map
        maps duplicate model names to their canonical equivalents
    """
    deduplicated_models: dict[str, Any] = {}
    reference_map: dict[str, str] = {}

    # Compare models to detect duplicates
    for model_name, model in models.items():
        found_duplicate = False

        # Compare with already deduplicated models
        for dedup_model_name, dedup_model in deduplicated_models.items():
            # Handle BaseModel types
            if isinstance(model, type) and isinstance(dedup_model, type) and are_models_equal(model, dedup_model):
                reference_map[model_name] = dedup_model_name
                found_duplicate = True
                logging.info(f"Model '{model_name}' is a duplicate of '{dedup_model_name}'")
                break

            # Handle RootModel[list[X]] - Check if both are RootModel wrapping lists
            try:
                # Check if both are RootModel subclasses with list types
                if (
                    isinstance(model, type)
                    and issubclass(model, RootModel)
                    and isinstance(dedup_model, type)
                    and issubclass(dedup_model, RootModel)
                ):
                    # Get the root type (what RootModel wraps)
                    model_root = model.model_fields.get("root")
                    dedup_root = dedup_model.model_fields.get("root")

                    if model_root and dedup_root:
                        # Extract the inner type from list[X]
                        model_origin = get_origin(model_root.annotation)
                        dedup_origin = get_origin(dedup_root.annotation)

                        if model_origin is list and dedup_origin is list:
                            model_inner = (
                                get_args(model_root.annotation)[0] if get_args(model_root.annotation) else None
                            )
                            dedup_inner = (
                                get_args(dedup_root.annotation)[0] if get_args(dedup_root.annotation) else None
                            )

                            if model_inner and dedup_inner and model_inner == dedup_inner:
                                reference_map[model_name] = dedup_model_name
                                found_duplicate = True
                                logging.info(
                                    f"Model '{model_name}' is a duplicate RootModel[list[...]] of '{dedup_model_name}'"
                                )
                                break
            except (AttributeError, TypeError):
                pass  # Not a RootModel or doesn't have expected structure

            # Handle plain List models (generic list types, not RootModel)
            model_origin = get_origin(model)
            dedup_model_origin = get_origin(dedup_model)

            if model_origin in {list} and dedup_model_origin in {list}:
                model_inner_type = get_args(model)[0] if get_args(model) else None
                dedup_inner_type = get_args(dedup_model)[0] if get_args(dedup_model) else None

                # If the inner types of the lists are the same, consider them duplicates
                if model_inner_type and dedup_inner_type and model_inner_type == dedup_inner_type:
                    reference_map[model_name] = dedup_model_name
                    found_duplicate = True
                    logging.info(f"Model '{model_name}' is a duplicate list type of '{dedup_model_name}'")
                    break

        # If no duplicate found, keep the model
        if not found_duplicate:
            deduplicated_models[model_name] = model

    # Return the deduplicated models and reference map
    return deduplicated_models, reference_map


def update_model_references(models: dict[str, Any], reference_map: dict[str, str]) -> dict[str, Any]:
    """Update references in models based on the deduplication reference map, including nested generics.

    Args:
        models: Dictionary of model names to model classes
        reference_map: Mapping from duplicate model names to canonical names

    Returns:
        Updated models dictionary with references resolved
    """

    def resolve_model_reference(annotation: Any) -> Any:
        """Resolve references in the model recursively, including nested types."""
        origin = get_origin(annotation)
        args = get_args(annotation)

        # Handle Union, List, or any other generic types
        if origin in {Union, list, Optional} and args:
            # Recursively resolve references for the inner types
            resolved_inner_types = tuple(resolve_model_reference(arg) for arg in args)
            return origin[resolved_inner_types]

        # Handle direct references in the reference_map
        annotation_name = str(annotation).split(".")[-1].strip("'>")
        if annotation_name in reference_map:
            resolved_model = models[reference_map[annotation_name]]
            return resolved_model

        # If it's a normal type or not in the map, return as-is
        return annotation

    updated_models = {}

    for model_name, model in models.items():
        if model_name in reference_map:
            # If the model name is in the reference map, update its reference
            dedup_model_name = reference_map[model_name]
            updated_models[model_name] = models[dedup_model_name]
        else:
            # Handle RootModel classes - need to recreate with updated inner references
            if isinstance(model, type) and issubclass(model, RootModel):
                root_field = model.model_fields.get("root")
                if root_field:
                    # Resolve references in the root annotation
                    updated_annotation = resolve_model_reference(root_field.annotation)

                    # Check if the annotation actually changed
                    if updated_annotation != root_field.annotation:
                        # Recreate the RootModel with the updated type
                        updated_model = type(
                            model_name,
                            (RootModel[updated_annotation],),  # type: ignore[valid-type]
                            {"__module__": getattr(model, "__module__", __name__)},
                        )
                        updated_models[model_name] = updated_model
                    else:
                        # No change needed, keep original
                        updated_models[model_name] = model
                else:
                    # No root field, keep original
                    updated_models[model_name] = model
            else:
                # Recursively resolve references in model annotations if they are generic
                updated_models[model_name] = resolve_model_reference(model)

    return updated_models


def normalize_description(description: str) -> str:
    """
    Normalize a description string for use in Python code.

    - Replaces newlines with spaces
    - Collapses multiple spaces into single spaces
    - Strips leading/trailing whitespace

    Args:
        description: Raw description string from OpenAPI spec

    Returns:
        Normalized description string safe for Python code
    """
    if not description:
        return ""

    # Replace newlines with spaces
    normalized = description.replace("\n", " ")
    # Collapse multiple spaces
    normalized = " ".join(normalized.split())
    # Strip leading/trailing whitespace
    normalized = normalized.strip()

    return normalized


def escape_description_for_field(description: str) -> str:
    """
    Escape a description string for safe use in Field(description="...") parameter.

    Uses json.dumps() to properly escape all special characters including:
    - Double quotes
    - Backslashes
    - Newlines
    - Unicode characters

    Args:
        description: Description string to escape

    Returns:
        JSON-escaped string ready for Field() parameter (without outer quotes)
    """
    if not description:
        return ""

    # Normalize first
    normalized = normalize_description(description)
    if not normalized:
        return ""

    # Use json.dumps to escape all special characters
    # Remove the outer quotes added by json.dumps
    escaped = json.dumps(normalized)[1:-1]

    return escaped
