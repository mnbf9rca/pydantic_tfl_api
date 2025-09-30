"""
DEPRECATION WARNING: This script is deprecated and will be removed in a future version.

Please use the new modular build system instead:
    scripts/build_with_coordinator.py

The legacy monolithic build_models.py script has been superseded by a more maintainable,
modular architecture:
- scripts/build_system/build_coordinator.py - Orchestrates the build process
- scripts/build_system/spec_processor.py - Handles OpenAPI specification loading and processing
- scripts/build_system/model_builder.py - Creates Pydantic models from schemas
- scripts/build_system/dependency_resolver.py - Manages model dependencies
- scripts/build_system/file_manager.py - Handles all file I/O operations
- scripts/build_system/client_generator.py - Generates API client code
- scripts/build_system/utilities.py - Shared utility functions

All functions from this script have been migrated to the appropriate modules above.
"""
import warnings

warnings.warn(
    "build_models.py is deprecated. Use scripts/build_with_coordinator.py instead.",
    DeprecationWarning,
    stacklevel=2,
)

import argparse
import builtins
import json
import keyword
import logging
import os
import re
import shutil
import sys
import types
from collections import defaultdict
from enum import Enum
from io import TextIOWrapper
from pathlib import Path
from typing import (
    Any,
    ForwardRef,
    Optional,
    Union,
    cast,
    get_args,
    get_origin,
)
from typing import __all__ as typing_all
from urllib.parse import urljoin

from pydantic import BaseModel, Field, RootModel, create_model
from pydantic.fields import FieldInfo

try:
    from .mapping_loader import load_tfl_mappings
except ImportError:
    from mapping_loader import load_tfl_mappings  # type: ignore[import-not-found, no-redef]

# Load mappings from JSON
tfl_mappings = load_tfl_mappings()

src_path = os.path.join(os.path.dirname(__file__), "src")
sys.path.insert(0, src_path)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Helper functions
def sanitize_name(name: str, prefix: str = "Model") -> str:
    """
    Sanitize class names or field names to ensure they are valid Python identifiers.
    1. Replace invalid characters (like hyphens) with underscores.
    2. Extract the portion after the last underscore for more concise names.
    3. Prepend prefix if the name starts with a digit or is a Python keyword.
    """

    # Replace invalid characters (like hyphens) with underscores
    sanitized = re.sub(r"[^a-zA-Z0-9_ ]", "_", name)

    # Extract the portion after the last underscore for concise names
    sanitized = sanitized.split("_")[-1]

    # Convert to CamelCase
    words = sanitized.split()
    sanitized = words[0] + "".join(word.capitalize() for word in words[1:])

    # Prepend prefix if necessary (i.e., name starts with a digit or is a Python keyword)
    if sanitized[0].isdigit() or keyword.iskeyword(sanitized):
        sanitized = f"{prefix}_{sanitized}"

    return sanitized


def update_refs(obj: Any, entity_mapping: dict[str, str]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "$ref" and isinstance(value, str) and value.split("/")[-1] in entity_mapping:
                obj[key] = value.replace(value.split("/")[-1], entity_mapping[value.split("/")[-1]])
            else:
                update_refs(value, entity_mapping)
    elif isinstance(obj, list):
        for item in obj:
            update_refs(item, entity_mapping)


# Update entities and references
def update_entities(spec: dict[str, Any], api_name: str, pydantic_names: dict[str, str]) -> None:
    if api_name not in tfl_mappings:
        return

    entity_mapping = tfl_mappings[api_name]
    components = spec.get("components", {}).get("schemas", {})

    # Sanitize old and new names to match how they will be used in the models
    sanitized_entity_mapping = {old_name: sanitize_name(new_name) for old_name, new_name in entity_mapping.items()}

    # Rename entities in the schema components
    for old_name, new_name in sanitized_entity_mapping.items():
        if old_name in components:
            components[new_name] = components.pop(old_name)
            pydantic_names[old_name] = new_name

    # Update references recursively in the spec
    update_refs(spec, sanitized_entity_mapping)


def create_enum_class(enum_name: str, enum_values: list[Any]) -> type[Enum]:
    """Dynamically create a Pydantic Enum class for the given enum values."""

    def clean_enum_name(value: str) -> str:
        # Replace spaces and special characters with underscores and capitalize all letters
        return re.sub(r"\W|^(?=\d)", "_", value).strip("_").replace("-", "_").upper()

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
    field_spec: dict[str, Any],
    field_name: str,
    components: dict[str, Any],
    models: dict[str, type[BaseModel]],
) -> Any:
    if "$ref" in field_spec:
        # Handle references using ForwardRef for proper type resolution
        ref_name = sanitize_name(field_spec["$ref"].split("/")[-1])
        return ForwardRef(ref_name)

    openapi_type: str = field_spec.get("type", "Any")

    # Handle enums with mixed types
    if "enum" in field_spec:
        enum_values = field_spec["enum"]
        # Capitalize just the first letter of the field name, leave the rest as is
        cap_field_name = field_name[0].upper() + field_name[1:]
        enum_name = f"{cap_field_name}Enum"
        # Dynamically create an enum class and return it
        return create_enum_class(enum_name, enum_values)

    # Handle arrays
    if openapi_type == "array":
        # Ensure that 'items' exist for arrays, fallback to Any if missing
        items_spec = field_spec.get("items", {})
        if items_spec:
            inner_type = map_type(items_spec, field_name, components, models)
            # Use type: ignore since inner_type is a runtime value used as a type parameter
            return list[inner_type]  # type: ignore[valid-type]
        else:
            logging.warning("'items' missing in array definition, using Any")
            return list[Any]

    # Map standard OpenAPI types to Python types
    return map_openapi_type(openapi_type)


def map_openapi_type(openapi_type: str) -> type | Any:
    return {
        "string": str,
        "integer": int,
        "boolean": bool,
        "number": float,
        "object": dict,
        "array": list,
    }.get(openapi_type, Any)


def create_array_types_from_model_paths(paths: dict[str, dict[str, Any]], components: dict[str, Any]) -> dict[str, Any]:
    array_types = {}
    for _path, methods in paths.items():
        for _method, details in methods.items():
            operation_id = details.get("operationId")
            if operation_id:
                response_content = details["responses"]["200"]
                if "content" not in response_content:
                    continue

                response_type = response_content["content"]["application/json"]["schema"].get("type", "")
                if response_type == "array":
                    model_ref = response_content["content"]["application/json"]["schema"]["items"].get("$ref", "")
                    model_name = model_ref.split("/")[-1]
                    if model_name in components:
                        array_model_name = get_array_model_name(model_name)
                        array_types[array_model_name] = create_openapi_array_type(model_ref)
    return array_types


def get_array_model_name(model_name: str) -> str:
    return f"{sanitize_name(model_name)}Array"


def create_openapi_array_type(model_ref: str) -> dict[str, Any]:
    return {"type": "array", "items": {"$ref": f"{model_ref}"}}


# Create Pydantic models
def create_pydantic_models(components: dict[str, Any], models: dict[str, type[BaseModel] | type]) -> None:
    # First pass: create object models
    for model_name, model_spec in components.items():
        sanitized_name = sanitize_name(model_name)  # Ensure the model name is valid
        if model_spec.get("type") == "object":
            if "properties" not in model_spec:
                # Fallback if 'properties' is missing
                # just create a List model which accepts any dict
                models[sanitized_name] = dict[str, Any]
                logging.warning(f"Object model {sanitized_name} has no valid 'properties'. Using dict[str, Any].")
                continue
            # Handle object models first
            fields: dict[str, Any] = {}
            required_fields = model_spec.get("required", [])
            for field_name, field_spec in model_spec["properties"].items():
                field_type = map_type(field_spec, field_name, components, models)  # Map the OpenAPI type to Python type
                sanitized_field_name = sanitize_field_name(field_name)
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
            models[sanitized_name] = create_model(sanitized_name, **fields)
            logging.info(f"Created object model: {sanitized_name}")

    # Second pass: handle array models referencing the object models
    for model_name, model_spec in components.items():
        sanitized_name = sanitize_name(model_name)
        if model_spec.get("type") == "array":
            # Handle array models
            items_spec = model_spec.get("items")
            if "$ref" in items_spec:
                # Handle reference in 'items'
                ref_model_name = sanitize_name(items_spec["$ref"].split("/")[-1])
                if ref_model_name not in models:
                    raise KeyError(
                        f"Referenced model '{ref_model_name}' not found while creating array '{sanitized_name}'"
                    )
                models[sanitized_name] = list[models[ref_model_name]]  # type: ignore[valid-type]  # Create list type for array items
                logging.info(f"Created array model: {sanitized_name} -> list[{ref_model_name}]")
            else:
                # Fallback if 'items' is missing or doesn't have a reference
                models[sanitized_name] = list[Any]
                logging.warning(f"Array model {sanitized_name} has no valid 'items' reference. Using list[Any].")


def get_pydantic_imports(sanitized_model_name: str, is_root_model: bool) -> str:
    """Get the appropriate pydantic imports based on model type and name."""
    base_imports = ["RootModel"] if is_root_model else ["BaseModel", "Field"]

    # Always include ConfigDict for consistent v2 patterns
    imports = base_imports + ["ConfigDict"]

    return f"from pydantic import {', '.join(imports)}"


def get_model_config(sanitized_model_name: str) -> str:
    """Get the appropriate model_config for the model."""
    return "model_config = ConfigDict(from_attributes=True)"


# Save models and config to files
def determine_typing_imports(
    model_fields: dict[str, FieldInfo],
    models: dict[str, type[BaseModel] | type],
    circular_models: set[str],
) -> list[str]:
    """Determine necessary typing imports based on the field annotations."""
    import_set = set()

    for field in model_fields.values():
        field_annotation = get_type_str(field.annotation, models)

        # Check for any type in typing.__all__
        for type_name in typing_all:
            if type_name in field_annotation:
                import_set.add(type_name)

        # Check for circular references
        if field_annotation in circular_models:
            import_set.add("ForwardRef")

    return list(import_set)


def write_import_statements(
    init_f: TextIOWrapper, models: dict[str, type[BaseModel]], models_dir: str, sorted_models: list[str] | None = None
) -> None:
    """Write import statements in dependency-aware order to minimize forward references."""
    # If we have a topologically sorted order, use it; otherwise fall back to alphabetical
    model_order = sorted_models or sorted(models.keys())

    # Write imports in dependency order to minimize forward references
    for model_name in model_order:
        if model_name in models:
            init_f.write(f"from .{model_name} import {model_name}\n")


def save_models(
    models: dict[str, type[BaseModel] | type[list]],
    base_path: str,
    dependency_graph: dict[str, set[str]],
    circular_models: set[str],
    sorted_models: list[str] | None = None,
) -> None:
    models_dir = os.path.join(base_path, "models")
    os.makedirs(models_dir, exist_ok=True)
    # existing_models = find_existing_models(models_dir)

    # all_models_to_import = {**models, **existing_models}

    init_file = os.path.join(models_dir, "__init__.py")
    with open(init_file, "w") as init_f:
        # Write import statements in dependency-aware order to minimize forward references
        write_import_statements(init_f, models, models_dir, sorted_models)

        # Import GenericResponseModel from core for backward compatibility
        init_f.write("from ..core.package_models import GenericResponseModel\n")

        for model_name, model in models.items():
            save_model_file(
                model_name,
                model,
                models,
                models_dir,
                dependency_graph,
                circular_models,
                init_f,
            )

        # Add ResponseModelName Literal type
        model_names_for_literal = ",\n    ".join(f'"{key}"' for key in sorted(models.keys()))
        init_f.write("from typing import Literal\n\n")
        init_f.write(f"ResponseModelName = Literal[\n    {model_names_for_literal}\n]\n\n")

        model_names = ",\n    ".join(f'"{key}"' for key in sorted(models.keys()))
        init_f.write(f"__all__ = [\n    {model_names}\n]\n")

    # Write enums after saving the models
    write_enum_files(models, models_dir)


def save_model_file(
    model_name: str,
    model: Any,
    models: dict[str, type[BaseModel]],
    models_dir: str,
    dependency_graph: dict[str, set[str]],
    circular_models: set[str],
    init_f: TextIOWrapper,
) -> None:
    sanitized_model_name = sanitize_name(model_name)
    model_file = os.path.join(models_dir, f"{sanitized_model_name}.py")
    os.makedirs(models_dir, exist_ok=True)

    # Files will be overwritten directly - git serves as our backup

    with open(model_file, "w") as mf:
        if is_list_or_dict_model(model):
            mf.write(f"{get_pydantic_imports(sanitized_model_name, is_root_model=True)}\n")
            handle_list_or_dict_model(
                mf,
                model,
                models,
                dependency_graph,
                circular_models,
                sanitized_model_name,
            )
        else:
            handle_regular_model(
                mf,
                model,
                models,
                dependency_graph,
                circular_models,
                sanitized_model_name,
            )

        init_f.write(f"from .{sanitized_model_name} import {sanitized_model_name}\n")


def get_builtin_types() -> set:
    """Return a set of all built-in Python types."""
    return {obj for name, obj in vars(builtins).items() if isinstance(obj, type)}


def is_list_or_dict_model(model: Any) -> str | None:
    """Determine if the model is a list or dict type and return the type string ('list' or 'dict')."""
    origin = get_origin(model)
    if origin is list:
        return "list"
    if origin is dict:
        return "dict"
    return None


def validate_list_dict_args(model_type: str, args: tuple) -> None:
    """Validate argument counts for list/dict models."""
    if model_type == "list" and len(args) != 1:
        raise ValueError(f"list type should have exactly 1 argument, got {len(args)}")
    elif model_type == "dict" and len(args) != 2:
        raise ValueError(f"dict type should have exactly 2 arguments (key, value), got {len(args)}")


def extract_list_dict_types(model_type: str, args: tuple) -> tuple[Any, Any | None, Any]:
    """Extract inner types from list/dict model arguments."""
    if model_type == "list":
        inner_type = args[0]
        key_type = None
        value_type = inner_type
    elif model_type == "dict":
        key_type = args[0]
        value_type = args[1]
        inner_type = value_type  # For backward compatibility
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    return inner_type, key_type, value_type


def collect_type_imports(
    type_obj: Any, models: dict[str, type[BaseModel]], typing_imports: set[str], module_imports: set[str]
) -> str:
    """Collect imports for a given type and return its name."""
    built_in_types = get_builtin_types()
    type_name = getattr(type_obj, "__name__", None)

    if type_name and type_name not in {"Optional", "list", "Union"}:
        sanitized_name = sanitize_name(type_name)
        if sanitized_name in models:
            module_imports.add(f"from .{sanitized_name} import {sanitized_name}")
        elif type_obj not in built_in_types:
            typing_imports.add(type_name)

    return type_name or "Any"


def generate_list_dict_class_definition(model_type: str, sanitized_model_name: str, type_names: dict[str, str]) -> str:
    """Generate class definition for list/dict models."""
    if model_type == "list":
        return f"class {sanitized_model_name}(RootModel[list[{type_names['inner']}]]):\n"
    elif model_type == "dict":
        return f"class {sanitized_model_name}(RootModel[dict[{type_names['key']}, {type_names['value']}]]):\n"
    else:
        raise ValueError("Model is not a list or dict model.")


def write_imports_and_class(
    model_file: TextIOWrapper,
    typing_imports: set[str],
    module_imports: set[str],
    class_definition: str,
    sanitized_model_name: str,
) -> None:
    """Write all imports and class definition to the model file."""
    # Write typing imports
    if typing_imports:
        clean_typing_imports = sorted(typing_imports - get_builtin_types())
        if clean_typing_imports:
            model_file.write(f"from typing import {', '.join(sorted(clean_typing_imports))}\n")

    # Write module imports
    if module_imports:
        model_file.write("\n".join(sorted(module_imports)) + "\n")

    # Write class definition
    model_file.write(f"\n\n{class_definition}")

    # Write model config
    model_file.write(f"\n    {get_model_config(sanitized_model_name)}\n")


def handle_list_or_dict_model(
    model_file: TextIOWrapper,
    model: Any,
    models: dict[str, type[BaseModel]],
    dependency_graph: dict[str, set[str]],
    circular_models: set[str],
    sanitized_model_name: str,
) -> None:
    """Handle models that are either list or dict types."""
    # Check if the model is a List or Dict
    model_type = is_list_or_dict_model(model)
    args = model.__args__

    # Validate and extract types using helper functions
    validate_list_dict_args(model_type, args)
    inner_type, key_type, value_type = extract_list_dict_types(model_type, args)

    # Collect imports
    typing_imports = {model_type.title() if model_type else ""}
    module_imports: set[str] = set()

    # Handle imports and get type names
    type_names = {}
    if model_type == "list":
        type_names["inner"] = collect_type_imports(inner_type, models, typing_imports, module_imports)
    elif model_type == "dict":
        type_names["key"] = collect_type_imports(key_type, models, typing_imports, module_imports)
        type_names["value"] = collect_type_imports(value_type, models, typing_imports, module_imports)

    # Generate and write class using helper functions
    class_definition = generate_list_dict_class_definition(model_type, sanitized_model_name, type_names)
    write_imports_and_class(model_file, typing_imports, module_imports, class_definition, sanitized_model_name)


def handle_regular_model(
    model_file: TextIOWrapper,
    model: BaseModel,
    models: dict[str, type[BaseModel]],
    dependency_graph: dict[str, set],
    circular_models: set[str],
    sanitized_model_name: str,
) -> None:
    # Check if the model is a RootModel
    is_root_model = isinstance(model, type) and issubclass(model, RootModel)

    # Determine necessary imports
    typing_imports = sorted(
        set(determine_typing_imports(model.model_fields, models, circular_models)) - get_builtin_types()
    )

    import_set = set()

    # Add typing imports only if there are any
    if typing_imports:
        import_set.add(f"from typing import {', '.join(typing_imports)}")

    # Add pydantic imports using helper function
    import_set.add(get_pydantic_imports(sanitized_model_name, is_root_model))

    # Write imports for referenced models
    referenced_models = dependency_graph.get(sanitized_model_name, set())
    for ref_model in referenced_models:
        if ref_model != sanitized_model_name and ref_model not in {
            "Optional",
            "list",
            "Union",
        }:
            import_set.add(f"from .{ref_model} import {ref_model}")

    # Add Enum imports
    import_set.update(find_enum_imports(model))

    # Write imports
    model_file.write("\n".join(sorted(import_set)) + "\n\n\n")

    # Write class definition
    if is_root_model:
        root_annotation = model.model_fields['root'].annotation
        annotation_name = root_annotation.__name__ if root_annotation is not None else 'Any'
        model_file.write(
            f"class {sanitized_model_name}(RootModel[{annotation_name}]):\n"
        )
    else:
        model_file.write(f"class {sanitized_model_name}(BaseModel):\n")
        write_model_fields(model_file, model, models, circular_models)

    # Pydantic model config
    model_file.write(f"\n    {get_model_config(sanitized_model_name)}\n")

    # Add model_rebuild() if circular dependencies exist
    if sanitized_model_name in circular_models:
        model_file.write(f"\n{sanitized_model_name}.model_rebuild()\n")


def find_enum_imports(model: BaseModel) -> set[str]:
    """Find all enum imports in the model fields."""
    import_set = set()
    for _field_name, field in model.model_fields.items():
        inner_types = extract_inner_types(field.annotation)
        for inner_type in inner_types:
            if isinstance(inner_type, type) and issubclass(inner_type, Enum):
                import_set.add(f"from .{inner_type.__name__} import {inner_type.__name__}")
    return import_set


def resolve_forward_refs_in_annotation(
    annotation: Any, models: dict[str, type[BaseModel]], circular_models: set[str]
) -> str:
    """
    Recursively resolve ForwardRef in an annotation to a string representation,
    handling Optional, List, and other generics, and quoting forward references.
    """
    import types

    origin = get_origin(annotation)
    args = get_args(annotation)

    # Handle Python 3.10+ union types (X | Y syntax) first
    if isinstance(annotation, types.UnionType):
        union_args = annotation.__args__
        if len(union_args) == 2 and type(None) in union_args:
            # It's an Optional type (X | None)
            non_none_arg = union_args[0] if union_args[0] is not type(None) else union_args[1]
            resolved_inner = resolve_forward_refs_in_annotation(non_none_arg, models, circular_models)
            return f"{resolved_inner} | None"
        else:
            # General union type (X | Y | Z)
            resolved_types = [resolve_forward_refs_in_annotation(arg, models, circular_models) for arg in union_args]
            return " | ".join(resolved_types)

    # Handle Optional as Union[T, NoneType] and convert it to Optional[T]
    if origin is Union and len(args) == 2 and type(None) in args:
        non_none_arg = args[0] if args[0] is not type(None) else args[1]
        resolved_inner = resolve_forward_refs_in_annotation(non_none_arg, models, circular_models)
        return f"Optional[{resolved_inner}]"

    if origin is None:
        # Base case: if it's a ForwardRef, return it quoted
        if isinstance(annotation, ForwardRef):
            return (
                f"'{annotation.__forward_arg__}'"
                if annotation.__forward_arg__ in circular_models
                else annotation.__forward_arg__
            )
        # Handle basic types including None
        if annotation is type(None):
            return "None"
        return annotation.__name__ if hasattr(annotation, "__name__") else str(annotation)

    # For generics like List, Dict, etc., resolve the inner types
    resolved_args = ", ".join(resolve_forward_refs_in_annotation(arg, models, circular_models) for arg in args)
    return f"{origin.__name__}[{resolved_args}]"


def write_model_fields(
    model_file: TextIOWrapper,
    model: BaseModel,
    models: dict[str, type[BaseModel]],
    circular_models: set[str],
) -> None:
    """Write the fields for the model."""
    for field_name, field in model.model_fields.items():
        sanitized_field_name = sanitize_field_name(field_name)

        # Resolve the field's annotation to get the type string, including handling ForwardRefs
        field_type = resolve_forward_refs_in_annotation(field.annotation, models, circular_models)

        # Only include alias if it differs from the original field name
        if field.alias and field.alias != field_name:
            model_file.write(f"    {sanitized_field_name}: {field_type} = Field(None, alias='{field.alias}')\n")
        else:
            model_file.write(f"    {sanitized_field_name}: {field_type} = Field(None)\n")


def write_enum_files(models: dict[str, type[BaseModel]], models_dir: str) -> None:
    """Write enum files directly from the model's fields."""
    for model in models.values():
        if hasattr(model, "model_fields"):
            for field in model.model_fields.values():
                inner_types = extract_inner_types(field.annotation)
                for inner_type in inner_types:
                    if isinstance(inner_type, type) and issubclass(inner_type, Enum):
                        enum_name = inner_type.__name__
                        enum_file = os.path.join(models_dir, f"{enum_name}.py")
                        os.makedirs(models_dir, exist_ok=True)
                        with open(enum_file, "w") as ef:
                            ef.write("from enum import Enum\n\n\n")
                            ef.write(f"class {enum_name}(Enum):\n")
                            for enum_member in inner_type:
                                ef.write(f"    {enum_member.name} = '{enum_member.value}'\n")


def sanitize_field_name(field_name: str) -> str:
    """Sanitize field names that are Python reserved keywords."""
    if keyword.iskeyword(field_name):
        logging.info(f"Field name '{field_name}' is a Python keyword, sanitizing to '{field_name}_field'")
    return f"{field_name}_field" if keyword.iskeyword(field_name) else field_name


def get_type_str(annotation: Any, models: dict[str, type[BaseModel]]) -> str:
    """Convert the annotation to a valid Python type string for writing to a file, handling model references."""
    if isinstance(annotation, ForwardRef):
        # Handle ForwardRef directly by returning the forward-referenced name
        return annotation.__forward_arg__

    if isinstance(annotation, type):
        # Handle basic types (e.g., int, str, float)
        if annotation is type(None):
            return "None"
        return annotation.__name__

    # Handle Python 3.10+ union types (X | Y syntax)
    if isinstance(annotation, types.UnionType):
        args = annotation.__args__
        if len(args) == 2 and type(None) in args:
            # It's an Optional type (X | None)
            non_none_arg = args[0] if args[0] is not type(None) else args[1]
            return f"{get_type_str(non_none_arg, models)} | None"
        else:
            # General union type (X | Y | Z)
            inner_types = " | ".join(get_type_str(arg, models) for arg in args)
            return inner_types

    elif hasattr(annotation, "__origin__"):
        origin = annotation.__origin__
        args = annotation.__args__

        # Handle list (e.g., list[str], list[Casualty])
        if origin is list:
            inner_type = get_type_str(args[0], models)
            return f"list[{inner_type}]"

        # Handle dict (e.g., dict[str, int])
        elif origin is dict:
            key_type = get_type_str(args[0], models)
            value_type = get_type_str(args[1], models)
            return f"dict[{key_type}, {value_type}]"

        # Handle Optional and Union (e.g., Optional[int], Union[str, int])
        elif origin is Union:
            if len(args) == 2 and args[1] is type(None):
                # It's an Optional type
                return f"Optional[{get_type_str(args[0], models)}]"
            else:
                # General Union type
                inner_types = ", ".join(get_type_str(arg, models) for arg in args)
                return f"Union[{inner_types}]"

    elif hasattr(annotation, "__name__") and annotation.__name__ in models:
        # Handle references to other models (e.g., Casualty)
        return annotation.__name__

    return "Any"


def create_mermaid_class_diagram(dependency_graph: dict[str, set[str]], sort_order: list[str], output_file: str) -> None:
    with open(output_file, "w") as f:
        f.write("classDiagram\n")
        for model in sort_order:
            if model in dependency_graph:
                dependencies = sorted(dependency_graph[model])
                if dependencies:
                    for dep in dependencies:
                        f.write(f"    {model} --> {dep}\n")
                else:
                    f.write(f"    class {model}\n")
            else:
                f.write(f"    class {model}\n")


# Dependency handling and circular references
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
            return [Optional] + non_none_args
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


def build_dependency_graph(
    models: dict[str, type[BaseModel] | type[list]],
) -> dict[str, set[str]]:
    """Build a dependency graph where each model depends on other models."""
    graph = defaultdict(set)

    for model_name, model in models.items():
        if isinstance(model, type) and hasattr(model, "model_fields"):
            # Iterate over each field in the model
            for field in model.model_fields.values():
                # Recursively unwrap and extract the inner types
                inner_types = extract_inner_types(field.annotation)

                for inner_type in inner_types:
                    # Handle ForwardRef (string-based references)
                    if isinstance(inner_type, ForwardRef):
                        graph[model_name].add(inner_type.__forward_arg__)

                    # Handle direct model references
                    elif hasattr(inner_type, "__name__") and inner_type.__name__ in models:
                        graph[model_name].add(sanitize_name(inner_type.__name__))

                    # If it's a generic type, keep unwrapping
                    elif hasattr(inner_type, "__origin__"):
                        nested_types = extract_inner_types(inner_type)
                        for nested_type in nested_types:
                            if isinstance(nested_type, ForwardRef):
                                graph[model_name].add(nested_type.__forward_arg__)
                            elif hasattr(nested_type, "__name__") and nested_type.__name__ in models:
                                graph[model_name].add(sanitize_name(nested_type.__name__))

        # Handle List models (arrays)
        elif hasattr(model, "__origin__") and (model.__origin__ is list or model.__origin__ is dict):
            args = get_args(model)
            if args:
                inner_type = args[0]
            else:
                continue
            if hasattr(inner_type, "__name__") and inner_type.__name__ in models:
                graph[model_name].add(sanitize_name(inner_type.__name__))
        else:
            logging.warning(f"Model '{model_name}' is not a Pydantic model, dict or list type")

    # finally, add any models which have zero dependencies
    for model_name in models:
        if model_name not in graph:
            graph[model_name] = set()
    return graph


def handle_dependencies(models: dict[str, type[BaseModel]]) -> tuple[dict[str, set[str]], set[str], list[str]]:
    graph = build_dependency_graph(models)
    sorted_models = topological_sort(graph)
    circular_models = detect_circular_dependencies(graph)
    break_circular_dependencies(models, circular_models)
    return graph, circular_models, sorted_models


def topological_sort(graph: dict[str, set[str]]) -> list[str]:
    # Exclude Python built-in types from the graph
    built_in_types = get_builtin_types()
    sorted_graph = sorted(graph)

    # Filter out built-in types from the graph
    in_degree = {model: 0 for model in sorted_graph if model not in built_in_types}

    for model in sorted_graph:
        if model in built_in_types:
            continue  # Skip built-in types

        for dep in sorted(graph[model]):
            if dep not in built_in_types:
                if dep not in in_degree:
                    in_degree[dep] = 0
                in_degree[dep] += 1

    # Initialize the queue with nodes that have an in-degree of 0
    queue = sorted([model for model in in_degree if in_degree[model] == 0])
    sorted_models = []

    while queue:
        model = queue.pop(0)  # Use pop(0) instead of popleft() for deterministic behavior
        sorted_models.append(model)
        for dep in sorted(graph[model]):
            if dep in built_in_types:
                continue  # Skip built-in types
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)
        queue.sort()  # Sort the queue after each iteration

    if len(sorted_models) != len(in_degree):
        missing_models = sorted(set(in_degree.keys()) - set(sorted_models))
        logging.warning(f"Circular dependencies detected among models: {missing_models}")
        sorted_models.extend(missing_models)

    return sorted_models


def detect_circular_dependencies(graph: dict[str, set[str]]) -> set[str]:
    circular_models = set()
    visited = set()
    stack = set()

    # Use a copy of the graph's keys to avoid modifying the dictionary during iteration
    def visit(model: str) -> None:
        if model in visited:
            return
        if model in stack:
            circular_models.add(model)
            return
        stack.add(model)
        for dep in graph.get(model, []):
            visit(dep)
        stack.remove(model)
        visited.add(model)

    # Iterate over a copy of the graph's keys
    for model in list(graph.keys()):
        visit(model)

    return circular_models


def replace_circular_references(annotation: Any, circular_models: set[str]) -> Any:
    """Recursively replace circular model references in annotations with ForwardRef."""
    import types

    origin = get_origin(annotation)
    args = get_args(annotation)

    if not args:
        # Base case: simple type, check if it's circular
        if isinstance(annotation, type) and annotation.__name__ in circular_models:
            return ForwardRef(annotation.__name__)
        return annotation

    # Recurse into generic types
    new_args = tuple(replace_circular_references(arg, circular_models) for arg in args)

    if origin is None:
        return annotation

    # Handle different origin types
    if isinstance(origin, types.UnionType):
        # For Python 3.10+ union syntax (X | Y), reconstruct using modern syntax
        if len(new_args) == 2:
            return new_args[0] | new_args[1]
        else:
            # Fall back to Union for complex cases
            # Fall back to Union for complex multi-type unions
            import operator
            from functools import reduce

            return reduce(operator.or_, new_args)
    else:
        # For traditional generic types like List[T], Dict[K, V], etc.
        try:
            return origin[new_args]
        except TypeError as e:
            if "not subscriptable" in str(e):
                # Fallback for any other UnionType-like cases
                if hasattr(origin, "__name__") and "Union" in str(origin):
                    if len(new_args) == 2:
                        return new_args[0] | new_args[1]
                    else:
                        # Fall back to Union for complex multi-type unions
                        import operator
                        from functools import reduce

                        return reduce(operator.or_, new_args)
                # If we can't handle it, return the original annotation
                logging.warning(f"Could not reconstruct type {origin} with args {new_args}: {e}")
                return annotation
            raise


def break_circular_dependencies(models: dict[str, type[BaseModel]], circular_models: set[str]) -> None:
    """Replace circular references in models with ForwardRef."""
    for model_name in circular_models:
        model = models[model_name]
        for _field_name, field in model.model_fields.items():
            # Modify field.annotation directly
            field.annotation = replace_circular_references(field.annotation, circular_models)


# def break_circular_dependencies(
#     models: dict[str, type[BaseModel]], circular_models: set[str]
# ):
#     for model_name in circular_models:
#         for field_name, field in models[model_name].model_fields.items():
#             # Extract the inner types (e.g., the actual model or type) from the field annotation
#             inner_types = extract_inner_types(field.annotation)

#             changed = False  # Track if any circular dependency was detected

#             # Check for circular dependencies in the extracted inner types
#             for i, inner_type in enumerate(inner_types):
#                 if (
#                     isinstance(inner_type, type)
#                     and inner_type.__name__ in circular_models
#                 ):
#                     # Replace the circular dependency with ForwardRef
#                     inner_types[i] = ForwardRef(inner_type.__name__)
#                     changed = True  # Mark as changed since we replaced a circular dependency

#             # Only rebuild the field annotation if a change was made
#             if changed:
#                 field.annotation = rebuild_annotation_with_inner_types(
#                     field.annotation, inner_types
#                 )


# Load OpenAPI specs
def load_specs(folder_path: str) -> list[dict[str, Any]]:
    return [json.load(open(os.path.join(folder_path, f))) for f in os.listdir(folder_path) if f.endswith(".json")]


def get_api_name(spec: dict[str, Any]) -> str:
    return spec["info"]["title"]


# Combine components and paths from all OpenAPI specs
def combine_components_and_paths(
    specs: list[dict[str, Any]], pydantic_names: dict[str, str]
) -> tuple[dict[str, Any], dict[str, Any]]:
    combined_components = {}
    combined_paths = {}

    for spec in specs:
        api_name = get_api_name(spec)
        api_path = f"/{spec.get('servers', [{}])[0].get('url', '').split('/', 3)[3]}"
        logging.info(f"Processing {api_name}")
        update_entities(spec, api_name, pydantic_names)
        combined_components.update(spec.get("components", {}).get("schemas", {}))
        these_paths = spec.get("paths", {})
        # add /api_path to the paths
        for path, methods in these_paths.items():
            new_path = urljoin(f"{api_path}/", path.lstrip("/"))
            combined_paths[new_path] = methods
        # combined_paths.update(spec.get("paths", {}))

    return combined_components, combined_paths


def are_models_equal(model1: type[BaseModel], model2: type[BaseModel]) -> bool:
    """Check if two Pydantic models are equal based on their fields, types, and metadata."""
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
    models: dict[str, type[BaseModel] | type[list]],
) -> tuple[dict[str, type[BaseModel] | type], dict[str, str]]:
    """Deduplicate models by removing models with the same content."""
    deduplicated_models: dict[str, type[BaseModel] | type] = {}
    reference_map: dict[str, str] = {}

    # Compare models to detect duplicates
    for model_name, model in models.items():
        found_duplicate = False

        # Compare with already deduplicated models
        for dedup_model_name, dedup_model in deduplicated_models.items():
            if isinstance(model, type) and isinstance(dedup_model, type) and are_models_equal(model, dedup_model):
                reference_map[model_name] = dedup_model_name
                found_duplicate = True
                logging.info(f"Model '{model_name}' is a duplicate of '{dedup_model_name}'")
                break

            # Handle List models separately by comparing their inner types
            model_origin = get_origin(model)
            dedup_model_origin = get_origin(dedup_model)

            if model_origin in {list} and dedup_model_origin in {list}:
                model_inner_type = get_args(model)[0]
                dedup_inner_type = get_args(dedup_model)[0]

                # If the inner types of the lists are the same, consider them duplicates
                if model_inner_type == dedup_inner_type:
                    reference_map[model_name] = dedup_model_name
                    found_duplicate = True
                    logging.info(f"Model '{model_name}' is a duplicate of '{dedup_model_name}'")
                    break

        # If no duplicate found, keep the model
        if not found_duplicate:
            deduplicated_models[model_name] = model

    # Return the deduplicated models and reference map
    return deduplicated_models, reference_map


def update_model_references(
    models: dict[str, type[BaseModel] | type[list]], reference_map: dict[str, str]
) -> dict[str, type[BaseModel] | type[list]]:
    """Update references in models based on the deduplication reference map, including nested generics."""

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
            # Recursively resolve references in model annotations if they are generic
            updated_models[model_name] = resolve_model_reference(model)

    return updated_models


def join_url_paths(a: str, b: str) -> str:
    # Ensure the base path ends with a slash for urljoin to work properly
    return urljoin(a + "/", b.lstrip("/"))


def create_config(spec: dict[str, Any], output_path: str, base_url: str) -> None:
    class_name = f"{sanitize_name(get_api_name(spec))}Client"
    paths = spec.get("paths", {})

    config_lines = []
    api_path = "/" + spec.get("servers", [{}])[0].get("url", "").split("/", 3)[3]
    config_lines.append(f'base_url = "{base_url}"\n')
    config_lines.append("endpoints = {\n")

    for path, methods in paths.items():
        for _method, details in methods.items():
            operation_id = details.get("operationId")
            if operation_id:
                path_uri = join_url_paths(api_path, path)
                path_params = [param["name"] for param in details.get("parameters", []) if param["in"] == "path"]
                for i, param in enumerate(path_params):
                    path_uri = path_uri.replace(f"{{{param}}}", f"{{{i}}}")

                response_content = details["responses"].get("200", {})

                model_name = get_model_name_from_path(response_content)

                config_lines.append(f"    '{operation_id}': {{'uri': '{path_uri}', 'model': '{model_name}'}},\n")

    config_lines.append("}\n")

    config_file_path = os.path.join(output_path, f"{class_name}_config.py")
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)

    with open(config_file_path, "w") as config_file:
        config_file.writelines(config_lines)

    logging.info(f"Config file generated at: {config_file_path}")


def classify_parameters(
    parameters: list[dict[str, Any]],
) -> tuple[list[str], list[str]]:
    """Classify parameters into path and query parameters."""
    path_params = [param["name"] for param in parameters if param["in"] == "path"]
    query_params = [param["name"] for param in parameters if param["in"] == "query"]
    return path_params, query_params


def extract_api_metadata(spec: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    """Extract basic API metadata from OpenAPI spec."""
    paths = spec.get("paths", {})
    class_name = f"{sanitize_name(get_api_name(spec))}Client"
    api_path = "/" + spec.get("servers", [{}])[0].get("url", "").split("/", 3)[3]
    return class_name, api_path, paths


def create_method_signature(operation_id: str, parameters: list[dict], model_name: str) -> str:
    """Create method signature for a single API operation."""
    param_str = create_function_parameters(parameters)
    sanitized_operation_id = sanitize_name(operation_id, prefix="Query")
    return f"    def {sanitized_operation_id}(self, {param_str}) -> ResponseModel[{model_name}] | ApiError:\n"


def create_method_docstring(details: dict[str, Any], full_path: str, model_name: str, parameters: list[dict]) -> str:
    """Create docstring for a single API method."""
    description = details.get("description", "No description in the OpenAPI spec.")
    docstring = f"{description}\n"
    docstring = docstring + f"\n  Query path: `{full_path}`\n"
    docstring = docstring + f"\n  `ResponseModel.content` contains `models.{model_name}` type.\n"

    if parameters:
        docstring_parameters = "\n".join(
            [
                f"    `{sanitize_field_name(param['name'])}`: {map_openapi_type(param['schema']['type']).__name__} - {param.get('description', '')}. {('Example: `' + str(param.get('example', '')) + '`') if param.get('example') else ''}"
                for param in parameters
            ]
        )
    else:
        docstring_parameters = "        No parameters required."

    return f"        '''\n        {docstring}\n\n  Parameters:\n{docstring_parameters}\n        '''\n"


def create_method_implementation(operation_id: str, parameters: list[dict]) -> str:
    """Create method implementation for a single API operation."""
    path_params, query_params = classify_parameters(parameters)

    formatted_path_params = ", ".join([sanitize_field_name(param) for param in path_params])
    formatted_query_params = ", ".join([f"'{param}': {sanitize_field_name(param)}" for param in query_params])

    if formatted_query_params:
        query_params_dict = f"endpoint_args={{ {formatted_query_params} }}"
    else:
        query_params_dict = "endpoint_args=None"

    if path_params:
        return f"        return self._send_request_and_deserialize(base_url, endpoints['{operation_id}'], params=[{formatted_path_params}], {query_params_dict})\n\n"
    else:
        return f"        return self._send_request_and_deserialize(base_url, endpoints['{operation_id}'], {query_params_dict})\n\n"


def process_single_method(
    path: str, method: str, details: dict[str, Any], api_path: str, all_types: set, all_package_models: set
) -> str:
    """Process a single API method and return its complete definition."""
    operation_id = details.get("operationId")
    if not operation_id:
        return ""

    parameters = details.get("parameters", [])
    all_types.update([map_openapi_type(param["schema"]["type"]) for param in parameters])

    response_content = details["responses"].get("200", {})
    model_name = get_model_name_from_path(response_content)
    all_package_models.add(model_name)

    full_path = join_url_paths(api_path, path)

    # Build complete method definition
    method_lines = []
    method_lines.append(create_method_signature(operation_id, parameters, model_name))
    method_lines.append(create_method_docstring(details, full_path, model_name, parameters))
    method_lines.append(create_method_implementation(operation_id, parameters))

    return "".join(method_lines)


def generate_import_lines(class_name: str, all_types: set, all_package_models: set) -> list[str]:
    """Generate all import statements for the client class."""
    import_lines = []
    import_lines.append(f"from .{class_name}_config import endpoints, base_url\n")

    # Check if GenericResponseModel is needed and import from core
    needs_generic_response_model = "GenericResponseModel" in all_package_models
    if needs_generic_response_model:
        import_lines.append("from ..core import ApiError, ResponseModel, Client, GenericResponseModel\n")
        # Remove GenericResponseModel from models import
        all_package_models = all_package_models - {"GenericResponseModel"}
    else:
        import_lines.append("from ..core import ApiError, ResponseModel, Client\n")

    valid_type_imports = all_types - get_builtin_types()
    valid_type_import_strings = sorted([t.__name__ for t in valid_type_imports])
    if valid_type_import_strings:
        import_lines.append(f"from typing import {', '.join(valid_type_import_strings)}\n")

    if all_package_models:
        import_lines.append(f"from ..models import {', '.join(sorted(all_package_models))}\n")

    import_lines.append("\n")
    return import_lines


def create_class(spec: dict[str, Any], output_path: str) -> None:
    """Generate API client class from OpenAPI specification."""
    class_name, api_path, paths = extract_api_metadata(spec)

    all_types: set[str] = set()
    all_package_models: set[str] = set()
    method_lines = [f"class {class_name}(Client):\n"]

    # Process all API methods
    for path, methods in paths.items():
        for method, details in methods.items():
            method_definition = process_single_method(path, method, details, api_path, all_types, all_package_models)
            if method_definition:
                method_lines.append(method_definition)

    # Generate complete file
    import_lines = generate_import_lines(class_name, all_types, all_package_models)

    class_file_path = os.path.join(output_path, f"{class_name}.py")
    os.makedirs(os.path.dirname(class_file_path), exist_ok=True)

    with open(class_file_path, "w") as class_file:
        class_file.writelines(import_lines)
        class_file.writelines(method_lines)

    logging.info(f"Class file generated at: {class_file_path}")


def get_model_name_from_path(response_content: dict[str, Any], only_arrays: bool = False) -> str:
    if not response_content or "content" not in response_content:
        return "GenericResponseModel"

    content = response_content["content"]
    if "application/json" not in content:
        return "GenericResponseModel"

    json_content = content["application/json"]
    if "schema" not in json_content:
        return "GenericResponseModel"

    schema = json_content["schema"]
    response_type = schema.get("type", "")

    if response_type == "array":
        items_schema = schema.get("items", {})
        model_ref = items_schema.get("$ref", "")
        if not model_ref:
            return "GenericResponseModel"
        return get_array_model_name(sanitize_name(model_ref.split("/")[-1]))
    elif not only_arrays:
        model_ref = schema.get("$ref", "")
        if not model_ref:
            return "GenericResponseModel"
        return sanitize_name(model_ref.split("/")[-1])
    else:
        return "GenericResponseModel"


def create_function_parameters(parameters: list[dict[str, Any]]) -> str:
    """Create a string of function parameters, ensuring they are safe Python identifiers."""
    # Sort parameters to ensure required ones come first
    sorted_parameters = sorted(parameters, key=lambda param: not param.get("required", False))

    param_str = ", ".join(
        [
            f"{sanitize_field_name(param['name'])}: {map_openapi_type(param['schema']['type']).__name__} | None = None"
            if not param.get("required", False)
            else f"{sanitize_field_name(param['name'])}: {map_openapi_type(param['schema']['type']).__name__}"
            for param in sorted_parameters
        ]
    )
    return param_str


def save_classes(specs: list[dict[str, Any]], base_path: str, base_url: str) -> None:
    """Create config and class files for each spec in the specs list."""

    class_names = [f"{sanitize_name(get_api_name(spec))}Client" for spec in specs]
    init_file_path = os.path.join(base_path, "__init__.py")
    with open(init_file_path, "w") as init_file:
        # init_file.write(f"# {init_file_path}\n")
        class_names_joined = ",\n    ".join(class_names)
        init_file.write(f"from .endpoints import (\n    {class_names_joined}\n)\n")
        # init_file.write("\n".join([f"from .endpoints.{name} import {name}" for name in class_names]))
        # init_file.write("from ..core import Client\n")
        # init_file.write("from ..core import RestClient\n")
        init_file.write("from . import models\n")
        init_file.write("from .core import __version__\n")

        # init_file.write("from .models import ApiError, GenericResponseModel, ResponseModel\n")
        # other_classes = ["Client", "RestClient", "ApiError", "GenericResponseModel", "ResponseModel"]
        init_file.write("\n__all__ = [\n")
        init_file.write(",\n".join([f"    '{name}'" for name in class_names]))
        # init_file.write(",\n".join([f"    '{name}'" for name in other_classes]))
        init_file.write(",\n    'models',\n    '__version__'\n]\n")

    endpoint_path = os.path.join(base_path, "endpoints")
    os.makedirs(endpoint_path, exist_ok=True)
    endpoint_init_file = os.path.join(endpoint_path, "__init__.py")
    with open(endpoint_init_file, "w") as endpoint_init:
        # endpoint_init.write(f"# {endpoint_init_file}\n")
        endpoint_init.write("from typing import Literal\n\n")
        endpoint_init.write("\n".join([f"from .{name} import {name}" for name in class_names]))
        endpoint_init.write("\n\n")

        # Generate TfLEndpoint Literal type
        endpoint_names = ",\n    ".join(f"'{name}'" for name in class_names)
        endpoint_init.write(f"TfLEndpoint = Literal[\n    {endpoint_names}\n]\n\n")

        endpoint_init.write("__all__ = [\n")
        endpoint_init.write(",\n".join([f"    '{name}'" for name in class_names]))
        endpoint_init.write("\n]\n")

    for spec in specs:
        api_name = get_api_name(spec)
        logging.info(f"Creating config and class files for {api_name}...")

        create_config(spec, endpoint_path, base_url)
        create_class(spec, endpoint_path)

    logging.info("All classes and configs saved.")


def map_deduplicated_name(type_name: str, reference_map: dict[str, str]) -> str:
    if type_name in reference_map:
        return reference_map[type_name]
    return type_name


def _create_schema_name_mapping(combined_components: dict[str, Any]) -> dict[str, str]:
    """Create reverse mapping from sanitized names back to original schema names."""
    schema_name_mapping = {}
    for schema_name in combined_components:
        sanitized = sanitize_name(schema_name)
        schema_name_mapping[sanitized] = schema_name
    return schema_name_mapping


def _update_schema_with_reference_map(
    schema_name: str,
    schema: dict[str, Any],
    reference_map: dict[str, str],
    schema_name_mapping: dict[str, str],
    combined_components: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Update a single schema using the reference map."""
    sanitized_name = sanitize_name(schema_name)
    if sanitized_name in reference_map:
        # This is a duplicate, use the canonical model's schema
        canonical_name = reference_map[sanitized_name]
        # Find the original schema name for the canonical model
        if canonical_name in schema_name_mapping:
            original_schema_name = schema_name_mapping[canonical_name]
            return canonical_name, combined_components[original_schema_name]
        else:
            # Fallback: use the current schema but with canonical name
            return canonical_name, schema
    else:
        return sanitized_name, schema


def _update_schemas_in_spec(
    spec: dict[str, Any],
    combined_components: dict[str, Any],
    reference_map: dict[str, str],
    schema_name_mapping: dict[str, str],
) -> None:
    """Update all schemas in a spec using the reference map."""
    if "components" in spec and "schemas" in spec["components"]:
        updated_schemas = {}
        for schema_name, schema in spec["components"]["schemas"].items():
            new_name, new_schema = _update_schema_with_reference_map(
                schema_name, schema, reference_map, schema_name_mapping, combined_components
            )
            updated_schemas[new_name] = new_schema
        spec["components"]["schemas"] = updated_schemas


def _update_reference_in_schema(schema: dict[str, Any], reference_map: dict[str, str]) -> None:
    """Update a single schema reference using the reference map."""
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        sanitized_ref = sanitize_name(ref)
        if sanitized_ref in reference_map:
            schema["$ref"] = f"#/components/schemas/{reference_map[sanitized_ref]}"
    elif schema.get("type") == "array" and "$ref" in schema.get("items", {}):
        ref = schema["items"]["$ref"].split("/")[-1]
        sanitized_ref = sanitize_name(ref)
        if sanitized_ref in reference_map:
            schema["items"]["$ref"] = f"#/components/schemas/{reference_map[sanitized_ref]}"


def _update_paths_in_spec(spec: dict[str, Any], reference_map: dict[str, str]) -> None:
    """Update all path references in a spec using the reference map."""
    if "paths" in spec:
        for path in spec["paths"].values():
            for method in path.values():
                if "responses" in method:
                    for response in method["responses"].values():
                        if "content" in response and "application/json" in response["content"]:
                            schema = response["content"]["application/json"].get("schema", {})
                            _update_reference_in_schema(schema, reference_map)


def update_specs_with_model_changes(
    specs: list[dict[str, Any]],
    combined_components: dict[str, Any],
    reference_map: dict[str, str],
) -> list[dict[str, Any]]:
    """Update specs with model changes by applying reference mappings."""
    updated_specs = []
    schema_name_mapping = _create_schema_name_mapping(combined_components)

    for spec in specs:
        updated_spec = spec.copy()
        _update_schemas_in_spec(updated_spec, combined_components, reference_map, schema_name_mapping)
        _update_paths_in_spec(updated_spec, reference_map)
        updated_specs.append(updated_spec)

    return updated_specs


# Main function
def _validate_and_setup_paths(spec_path: str, output_path: str) -> None:
    """Validate input paths and create output directory."""
    if not os.path.exists(spec_path):
        raise FileNotFoundError(f"Specification path does not exist: {spec_path}")

    logging.info(f"Starting model generation from {spec_path} to {output_path}")
    os.makedirs(output_path, exist_ok=True)


def _load_and_process_specs(spec_path: str) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    """Load OpenAPI specs and process components and paths."""
    logging.info("Loading OpenAPI specs...")
    specs = load_specs(spec_path)
    if not specs:
        raise ValueError(f"No valid specifications found in {spec_path}")

    logging.info("Generating components...")
    pydantic_names: dict[str, str] = {}
    combined_components, combined_paths = combine_components_and_paths(specs, pydantic_names)

    logging.info("Creating array types from model paths...")
    # some paths have an array type as a response, we need to handle these separately
    array_types = create_array_types_from_model_paths(combined_paths, combined_components)
    combined_components.update(array_types)

    return specs, combined_components, combined_paths


def _generate_and_process_models(combined_components: dict[str, Any]) -> tuple[dict[str, type[BaseModel] | type], dict[str, str]]:
    """Generate Pydantic models and process them for deduplication."""
    logging.info("Generating Pydantic models...")
    models: dict[str, type[BaseModel] | type] = {}
    create_pydantic_models(combined_components, models)

    # Deduplicate models before saving them
    logging.info("Deduplicating models...")
    deduplicated_models, reference_map = deduplicate_models(models)

    # Update model references
    models = update_model_references(deduplicated_models, reference_map)

    return models, reference_map


def _handle_dependencies_and_save_models(
    models: dict[str, Any], output_path: str
) -> tuple[dict[str, set[str]], set[str], list[str]]:
    """Handle model dependencies and save models to files."""
    logging.info("Handling dependencies...")
    dependency_graph, circular_models, sorted_models = handle_dependencies(models)

    # Now save the deduplicated models
    logging.info("Saving models to files...")
    save_models(models, output_path, dependency_graph, circular_models, sorted_models)

    return dependency_graph, circular_models, sorted_models


def _generate_classes_and_diagrams(
    specs: list[dict[str, Any]],
    combined_components: dict[str, Any],
    reference_map: dict[str, str],
    output_path: str,
    dependency_graph: dict[str, list[str]],
    sorted_models: list[str],
) -> None:
    """Generate API classes and create documentation diagrams."""
    # Create config and class
    logging.info("Creating config and class files...")
    base_url = "https://api.tfl.gov.uk"
    logging.info("Updating specs with model changes...")
    updated_specs = update_specs_with_model_changes(specs, combined_components, reference_map)

    save_classes(updated_specs, output_path, base_url)

    logging.info("Creating Mermaid class diagram...")
    create_mermaid_class_diagram(dependency_graph, sorted_models, os.path.join(output_path, "class_diagram.mmd"))


def copy_infrastructure(output_path: str) -> None:
    """
    Copy hand-crafted infrastructure components to the output directory.

    This function copies the core infrastructure files (client.py, package_models.py, etc.)
    from the infrastructure/core directory to the output directory, ensuring that
    generated code has access to the necessary infrastructure components.

    Args:
        output_path: Directory where infrastructure should be copied

    Raises:
        FileNotFoundError: If infrastructure directory doesn't exist
        PermissionError: If unable to copy files
    """
    # Get the directory containing this script (should be project root/scripts)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    infrastructure_dir = project_root / "infrastructure" / "core"

    if not infrastructure_dir.exists():
        raise FileNotFoundError(f"Infrastructure directory not found: {infrastructure_dir}")

    output_core_dir = Path(output_path) / "core"

    logging.info(f"Copying infrastructure from {infrastructure_dir} to {output_core_dir}")

    # Create output core directory and copy all infrastructure files
    output_core_dir.mkdir(parents=True, exist_ok=True)

    for infrastructure_file in infrastructure_dir.glob("*.py"):
        destination = output_core_dir / infrastructure_file.name

        shutil.copy2(infrastructure_file, destination)
        logging.info(f"Copied infrastructure: {infrastructure_file.name}")


def main(spec_path: str, output_path: str) -> None:
    """
    Main function to build Pydantic models from OpenAPI specifications.

    Args:
        spec_path: Path to the directory containing OpenAPI specification files
        output_path: Path to the directory where generated models will be saved

    Raises:
        FileNotFoundError: If spec_path doesn't exist
        ValueError: If specs are invalid or malformed
        Exception: For any other errors during model generation
    """
    try:
        _validate_and_setup_paths(spec_path, output_path)
        copy_infrastructure(output_path)
        specs, combined_components, combined_paths = _load_and_process_specs(spec_path)
        models, reference_map = _generate_and_process_models(combined_components)
        dependency_graph, circular_models, sorted_models = _handle_dependencies_and_save_models(models, output_path)
        _generate_classes_and_diagrams(
            specs, combined_components, reference_map, output_path, dependency_graph, sorted_models
        )

        logging.info(f"Model generation completed successfully. Generated {len(models)} models.")

    except FileNotFoundError as e:
        logging.error(f"File not found error: {e}")
        raise
    except ValueError as e:
        logging.error(f"Value error during model generation: {e}")
        raise
    except PermissionError as e:
        logging.error(f"Permission error accessing files: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during model generation: {e}", exc_info=True)
        raise RuntimeError(f"Model generation failed: {e}") from e

    logging.info("Processing complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process OpenAPI spec and generate output.")
    parser.add_argument("specpath", help="Path to the OpenAPI specification file")
    parser.add_argument("output", help="Path to the output file")

    args = parser.parse_args()

    main(args.specpath, args.output)
