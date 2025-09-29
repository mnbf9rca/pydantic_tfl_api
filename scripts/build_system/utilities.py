"""Shared utility functions for the build system."""

import builtins
import keyword
import re
from typing import Any, Union, get_args, get_origin


def sanitize_name(name: str, prefix: str = "Model") -> str:
    """
    Sanitize class names or field names to ensure they are valid Python identifiers.

    1. Replace invalid characters (like hyphens) with underscores.
    2. Extract the portion after the last underscore for more concise names.
    3. Prepend prefix if the name starts with a digit or is a Python keyword.

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
        sanitized = ''.join(word.capitalize() for word in words)
    elif words:
        sanitized = words[0]

    # Extract the portion after the last underscore for concise names
    if '_' in sanitized:
        sanitized = sanitized.split("_")[-1]

    # Convert to CamelCase if it's all lowercase
    if sanitized and sanitized.islower():
        sanitized = sanitized.capitalize()

    # Prepend prefix if necessary (i.e., name starts with a digit or is a Python keyword)
    if sanitized and (sanitized[0].isdigit() or keyword.iskeyword(sanitized.lower())):
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

    # If it's a Union (e.g., Optional), check for NoneType and return Optional
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
    return re.sub(r"\W|^(?=\d)", "_", value).strip("_").replace("-", "_").upper()


def join_url_paths(a: str, b: str) -> str:
    """Join URL paths ensuring proper slash handling."""
    from urllib.parse import urljoin
    # Ensure the base path ends with a slash for urljoin to work properly
    return urljoin(a + "/", b.lstrip("/"))
