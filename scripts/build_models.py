import json
import os
from io import TextIOWrapper
import sys
import logging
import inspect
import ast
import importlib.util
import re
import keyword
import builtins
import argparse
from collections import deque
from urllib.parse import urljoin

from typing import __all__ as typing_all

from enum import Enum
from typing import (
    Dict,
    Any,
    Optional,
    Union,
    Type,
    List,
    Set,
    get_origin,
    get_args,
    Literal,
    ForwardRef,
    Tuple,
)
from pydantic import BaseModel, RootModel, create_model, Field, ConfigDict
from pydantic.fields import FieldInfo
from datetime import datetime
from collections import defaultdict, deque
try:
    from .mapping_loader import load_tfl_mappings
except ImportError:
    from mapping_loader import load_tfl_mappings

# Load mappings from JSON
tfl_mappings = load_tfl_mappings()

src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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


def update_refs(obj: Any, entity_mapping: Dict[str, str]):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "$ref" and isinstance(value, str) and value.split("/")[-1] in entity_mapping:
                obj[key] = value.replace(
                    value.split("/")[-1], entity_mapping[value.split("/")[-1]]
                )
            else:
                update_refs(value, entity_mapping)
    elif isinstance(obj, list):
        for item in obj:
            update_refs(item, entity_mapping)


# Update entities and references
def update_entities(
    spec: Dict[str, Any], api_name: str, pydantic_names: Dict[str, str]
) -> None:
    if api_name not in tfl_mappings:
        return

    entity_mapping = tfl_mappings[api_name]
    components = spec.get("components", {}).get("schemas", {})

    # Sanitize old and new names to match how they will be used in the models
    sanitized_entity_mapping = {
        old_name: sanitize_name(new_name)
        for old_name, new_name in entity_mapping.items()
    }

    # Rename entities in the schema components
    for old_name, new_name in sanitized_entity_mapping.items():
        if old_name in components:
            components[new_name] = components.pop(old_name)
            pydantic_names[old_name] = new_name

    # Update references recursively in the spec
    update_refs(spec, sanitized_entity_mapping)


def create_enum_class(enum_name: str, enum_values: List[Any]) -> Type[Enum]:
    """Dynamically create a Pydantic Enum class for the given enum values."""

    def clean_enum_name(value: str) -> str:
        # Replace spaces and special characters with underscores and capitalize all letters
        return re.sub(r"\W|^(?=\d)", "_", value).strip("_").replace("-", "_").upper()

    # Create a dictionary with cleaned enum names as keys and the original values as values
    # Handle uniqueness by adding suffix for duplicates
    enum_dict = {}
    name_counts = {}

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
    return Enum(enum_name, enum_dict)


def map_type(
    field_spec: Dict[str, Any],
    field_name: str,
    components: Dict[str, Any],
    models: Dict[str, Type[BaseModel]],
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
            return List[map_type(items_spec, field_name, components, models)]
        else:
            logging.warning(f"'items' missing in array definition, using Any")
            return List[Any]

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


def create_array_types_from_model_paths(
    paths: Dict[str, Dict[str, Any]], components: Dict[str, Any]
) -> Dict[str, Any]:
    array_types = {}
    for path, methods in paths.items():
        for method, details in methods.items():
            operation_id = details.get("operationId")
            if operation_id:
                response_content = details["responses"]["200"]
                if "content" not in response_content:
                    continue

                response_type = response_content["content"]["application/json"][
                    "schema"
                ].get("type", "")
                if response_type == "array":
                    model_ref = response_content["content"]["application/json"][
                        "schema"
                    ]["items"].get("$ref", "")
                    model_name = model_ref.split("/")[-1]
                    if model_name in components:
                        array_model_name = get_array_model_name(model_name)
                        array_types[array_model_name] = create_openapi_array_type(
                            model_ref
                        )
    return array_types


def get_array_model_name(model_name: str) -> str:
    return f"{sanitize_name(model_name)}Array"


def create_openapi_array_type(model_ref: str) -> Dict[str, Any]:
    return {"type": "array", "items": {"$ref": f"{model_ref}"}}


# Create Pydantic models
def create_pydantic_models(
    components: Dict[str, Any], models: Dict[str, Type[BaseModel] | type]
) -> None:
    # First pass: create object models
    for model_name, model_spec in components.items():
        sanitized_name = sanitize_name(model_name)  # Ensure the model name is valid
        if model_spec.get("type") == "object":
            if "properties" not in model_spec:
                # Fallback if 'properties' is missing
                # just create a List model which accepts any dict
                models[sanitized_name] = Dict[str, Any]
                logging.warning(
                    f"Object model {sanitized_name} has no valid 'properties'. Using Dict[str, Any]."
                )
                continue
            # Handle object models first
            fields = {}
            required_fields = model_spec.get("required", [])
            for field_name, field_spec in model_spec["properties"].items():
                field_type = map_type(
                    field_spec, field_name, components, models
                )  # Map the OpenAPI type to Python type
                sanitized_field_name = sanitize_field_name(field_name)
                if field_name in required_fields:
                    fields[sanitized_field_name] = (
                        field_type,
                        Field(..., alias=field_name),
                    )
                else:
                    fields[sanitized_field_name] = (
                        Optional[field_type],
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
                models[sanitized_name] = List[
                    models[ref_model_name]
                ]  # Create List type for array items
                logging.info(
                    f"Created array model: {sanitized_name} -> List[{ref_model_name}]"
                )
            else:
                # Fallback if 'items' is missing or doesn't have a reference
                models[sanitized_name] = List[Any]
                logging.warning(
                    f"Array model {sanitized_name} has no valid 'items' reference. Using List[Any]."
                )


def create_generic_response_model() -> Type[RootModel]:
    class GenericResponseModel(RootModel):
        root: Any

        model_config = ConfigDict(arbitrary_types_allowed=True)

    return GenericResponseModel


# Save models and config to files
def determine_typing_imports(
    model_fields: Dict[str, FieldInfo],
    models: Dict[str, Type[BaseModel] | type],
    circular_models: Set[str],
) -> List[str]:
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

    return import_set


def write_import_statements(
    init_f: TextIOWrapper,
    models: Dict[str, Type[BaseModel]],
    models_dir: str,
    sorted_models: List[str] = None
):
    """Write import statements in dependency-aware order to minimize forward references."""
    # If we have a topologically sorted order, use it; otherwise fall back to alphabetical
    if sorted_models:
        model_order = sorted_models
    else:
        model_order = sorted(models.keys())

    # Write imports in dependency order to minimize forward references
    for model_name in model_order:
        if model_name in models:
            init_f.write(f"from .{model_name} import {model_name}\n")

def save_models(
    models: Dict[str, Union[Type[BaseModel], Type[List]]],
    base_path: str,
    dependency_graph: Dict[str, Set[str]],
    circular_models: Set[str],
    sorted_models: List[str] = None,
):
    models_dir = os.path.join(base_path, "models")
    os.makedirs(models_dir, exist_ok=True)
    # existing_models = find_existing_models(models_dir)

    # all_models_to_import = {**models, **existing_models}

    init_file = os.path.join(models_dir, "__init__.py")
    with open(init_file, "w") as init_f:
        # Write import statements in dependency-aware order to minimize forward references
        write_import_statements(init_f, models, models_dir, sorted_models)

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

        model_names = ',\n    '.join(f'"{key}"' for key in sorted(models.keys()))
        init_f.write(
            f"\n__all__ = [\n    {model_names}\n]\n"
        )

    # Write enums after saving the models
    write_enum_files(models, models_dir)


def save_model_file(
    model_name: str,
    model: Any,
    models: Dict[str, Type[BaseModel]],
    models_dir: str,
    dependency_graph: Dict[str, Set[str]],
    circular_models: Set[str],
    init_f,
):
    sanitized_model_name = sanitize_name(model_name)
    model_file = os.path.join(models_dir, f"{sanitized_model_name}.py")
    os.makedirs(models_dir, exist_ok=True)

    # Files will be overwritten directly - git serves as our backup

    with open(model_file, "w") as mf:
        if is_list_or_dict_model(model):
            if sanitized_model_name == "GenericResponseModel":
                mf.write("from pydantic import RootModel, ConfigDict\n")
            else:
                mf.write("from pydantic import RootModel\n")
            handle_list_or_dict_model(
                mf,
                model,
                models,
                dependency_graph,
                circular_models,
                sanitized_model_name,
            )
        else:
            # mf.write("from pydantic import BaseModel, Field\n")
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
    """Determine if the model is a list or dict type and return the type string ('List' or 'Dict')."""
    origin = get_origin(model)
    if origin is list:
        return "List"
    if origin is dict or origin is Dict:
        return "Dict"
    return None


def handle_list_or_dict_model(
    model_file: TextIOWrapper,
    model: Any,
    models: Dict[str, Type[BaseModel]],
    dependency_graph: Dict[str, set[str]],
    circular_models: Set[str],
    sanitized_model_name: str,
):
    """Handle models that are either list or dict types."""
    # Check if the model is a List or Dict
    model_type = is_list_or_dict_model(model)
    args = model.__args__

    # Validate argument counts
    if model_type == "List" and len(args) != 1:
        raise ValueError(f"List type should have exactly 1 argument, got {len(args)}")
    elif model_type == "Dict" and len(args) != 2:
        raise ValueError(f"Dict type should have exactly 2 arguments (key, value), got {len(args)}")

    # Extract inner types based on model type
    if model_type == "List":
        inner_type = args[0]
        key_type = None
        value_type = inner_type
    elif model_type == "Dict":
        key_type = args[0]
        value_type = args[1]
        inner_type = value_type  # For backward compatibility, keep inner_type as value_type
    # Separate sets for typing imports and module imports
    typing_imports = {model_type}
    module_imports = set()

    # Handle non-built-in types for both key and value types (for Dict) or inner_type (for List)
    built_in_types = get_builtin_types()

    def handle_type_imports(type_obj):
        """Helper function to handle imports for a given type."""
        type_name = getattr(type_obj, "__name__", None)
        if type_name and type_name not in {"Optional", "List", "Union"}:
            sanitized_name = sanitize_name(type_name)
            if sanitized_name in models:
                module_imports.add(f"from .{sanitized_name} import {sanitized_name}")
            elif type_obj not in built_in_types:
                typing_imports.add(type_name)
        return type_name or "Any"

    # Handle imports and get type names
    if model_type == "List":
        inner_type_name = handle_type_imports(inner_type)
    elif model_type == "Dict":
        key_type_name = handle_type_imports(key_type)
        value_type_name = handle_type_imports(value_type)

    # create the class definition
    if model_type == "List":
        class_definition = (
            f"class {sanitized_model_name}(RootModel[List[{inner_type_name}]]):\n"
        )
    elif model_type == "Dict":
        class_definition = f"class {sanitized_model_name}(RootModel[Dict[{key_type_name}, {value_type_name}]]):\n"
    else:
        raise ValueError("Model is not a list or dict model.")
    # Write typing imports
    if typing_imports:
        typing_imports = sorted(typing_imports - get_builtin_types())
        model_file.write(f"from typing import {', '.join(sorted(typing_imports))}\n")

    # Write module imports
    if module_imports:
        model_file.write("\n".join(sorted(module_imports)) + "\n")

    # Write class definition
    model_file.write(f"\n\n{class_definition}")

    # Use different model_config for GenericResponseModel
    if sanitized_model_name == "GenericResponseModel":
        model_file.write("\n    model_config = ConfigDict(arbitrary_types_allowed=True)\n")
    else:
        model_file.write("\n    model_config = {'from_attributes': True}\n")


def handle_regular_model(
    model_file: TextIOWrapper,
    model: BaseModel,
    models: Dict[str, Type[BaseModel]],
    dependency_graph: Dict[str, set],
    circular_models: Set[str],
    sanitized_model_name: str,
):
    # Check if the model is a RootModel
    is_root_model = isinstance(model, type) and issubclass(model, RootModel)

    # Determine necessary imports
    typing_imports = sorted(
        determine_typing_imports(model.model_fields, models, circular_models)
        - get_builtin_types()
    )

    import_set = {f"from typing import {', '.join(typing_imports)}"}

    # Add RootModel import if necessary
    if is_root_model:
        if sanitized_model_name == "GenericResponseModel":
            import_set.add("from pydantic import RootModel, ConfigDict")
        else:
            import_set.add("from pydantic import RootModel")
    else:
        if sanitized_model_name == "GenericResponseModel":
            import_set.add("from pydantic import BaseModel, Field, ConfigDict")
        else:
            import_set.add("from pydantic import BaseModel, Field")

    # Write imports for referenced models
    referenced_models = dependency_graph.get(sanitized_model_name, set())
    for ref_model in referenced_models:
        if ref_model != sanitized_model_name and ref_model not in {
            "Optional",
            "List",
            "Union",
        }:
            import_set.add(f"from .{ref_model} import {ref_model}")

    # Add Enum imports
    import_set.update(find_enum_imports(model))

    # Write imports
    model_file.write("\n".join(sorted(import_set)) + "\n\n\n")

    # Write class definition
    if is_root_model:
        model_file.write(
            f"class {sanitized_model_name}(RootModel[{model.model_fields['root'].annotation.__name__}]):\n"
        )
    else:
        model_file.write(f"class {sanitized_model_name}(BaseModel):\n")
        write_model_fields(model_file, model, models, circular_models)

    # Pydantic model config
    # Use different model_config for GenericResponseModel
    if sanitized_model_name == "GenericResponseModel":
        model_file.write("\n    model_config = ConfigDict(arbitrary_types_allowed=True)\n")
    else:
        model_file.write("\n    model_config = {'from_attributes': True}\n")

    # Add model_rebuild() if circular dependencies exist
    if sanitized_model_name in circular_models:
        model_file.write(f"\n{sanitized_model_name}.model_rebuild()\n")


def find_enum_imports(model: BaseModel) -> Set[str]:
    """Find all enum imports in the model fields."""
    import_set = set()
    for field_name, field in model.model_fields.items():
        inner_types = extract_inner_types(field.annotation)
        for inner_type in inner_types:
            if isinstance(inner_type, type) and issubclass(inner_type, Enum):
                import_set.add(
                    f"from .{inner_type.__name__} import {inner_type.__name__}"
                )
    return import_set


def resolve_forward_refs_in_annotation(annotation: Any, models: Dict[str, Type[BaseModel]], circular_models: Set[str]) -> str:
    """
    Recursively resolve ForwardRef in an annotation to a string representation, 
    handling Optional, List, and other generics, and quoting forward references.
    """
    origin = get_origin(annotation)
    args = get_args(annotation)

    # Handle Optional as Union[T, NoneType] and convert it to Optional[T]
    if origin is Union and len(args) == 2 and type(None) in args:
        non_none_arg = args[0] if args[0] is not type(None) else args[1]
        resolved_inner = resolve_forward_refs_in_annotation(non_none_arg, models, circular_models)
        return f"Optional[{resolved_inner}]"

    if origin is None:
        # Base case: if it's a ForwardRef, return it quoted
        if isinstance(annotation, ForwardRef):
            return f"'{annotation.__forward_arg__}'" if annotation.__forward_arg__ in circular_models else annotation.__forward_arg__
        return annotation.__name__ if hasattr(annotation, "__name__") else str(annotation)

    # For generics like List, Dict, etc., resolve the inner types
    resolved_args = ", ".join(resolve_forward_refs_in_annotation(arg, models, circular_models) for arg in args)
    return f"{origin.__name__}[{resolved_args}]"


def write_model_fields(
    model_file: TextIOWrapper,
    model: BaseModel,
    models: Dict[str, Type[BaseModel]],
    circular_models: Set[str],
):
    """Write the fields for the model."""
    for field_name, field in model.model_fields.items():
        sanitized_field_name = sanitize_field_name(field_name)

        # Resolve the field's annotation to get the type string, including handling ForwardRefs
        field_type = resolve_forward_refs_in_annotation(field.annotation, models, circular_models)

        # Only include alias if it differs from the original field name
        if field.alias and field.alias != field_name:
            model_file.write(
                f"    {sanitized_field_name}: {field_type} = Field(None, alias='{field.alias}')\n"
            )
        else:
            model_file.write(
                f"    {sanitized_field_name}: {field_type} = Field(None)\n"
            )

def write_enum_files(models: Dict[str, Type[BaseModel]], models_dir: str):
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
                                ef.write(
                                    f"    {enum_member.name} = '{enum_member.value}'\n"
                                )


def sanitize_field_name(field_name: str) -> str:
    """Sanitize field names that are Python reserved keywords."""
    if keyword.iskeyword(field_name):
        logging.info(f"Field name '{field_name}' is a Python keyword, sanitizing to '{field_name}_field'")
    return f"{field_name}_field" if keyword.iskeyword(field_name) else field_name


def get_type_str(annotation: Any, models: Dict[str, Type[BaseModel]]) -> str:
    """Convert the annotation to a valid Python type string for writing to a file, handling model references."""
    if isinstance(annotation, ForwardRef):
        # Handle ForwardRef directly by returning the forward-referenced name
        return annotation.__forward_arg__

    if isinstance(annotation, type):
        # Handle basic types (e.g., int, str, float)
        return annotation.__name__

    elif hasattr(annotation, "__origin__"):
        origin = annotation.__origin__
        args = annotation.__args__

        # Handle List (e.g., List[str], List[Casualty])
        if origin is list or origin is List:
            inner_type = get_type_str(args[0], models)
            return f"List[{inner_type}]"

        # Handle Dict (e.g., Dict[str, int])
        elif origin is dict or origin is Dict:
            key_type = get_type_str(args[0], models)
            value_type = get_type_str(args[1], models)
            return f"Dict[{key_type}, {value_type}]"

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


def create_mermaid_class_diagram(
    dependency_graph: Dict[str, Set[str]], sort_order: List[str], output_file: str
):
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
def extract_inner_types(annotation: Any) -> List[Any]:
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
    models: Dict[str, Union[Type[BaseModel], Type[List]]],
) -> Dict[str, Set[str]]:
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
                    elif (
                        hasattr(inner_type, "__name__")
                        and inner_type.__name__ in models
                    ):
                        graph[model_name].add(sanitize_name(inner_type.__name__))

                    # If it's a generic type, keep unwrapping
                    elif hasattr(inner_type, "__origin__"):
                        nested_types = extract_inner_types(inner_type)
                        for nested_type in nested_types:
                            if isinstance(nested_type, ForwardRef):
                                graph[model_name].add(nested_type.__forward_arg__)
                            elif (
                                hasattr(nested_type, "__name__")
                                and nested_type.__name__ in models
                            ):
                                graph[model_name].add(
                                    sanitize_name(nested_type.__name__)
                                )

        # Handle List models (arrays)
        elif hasattr(model, "__origin__") and (
            model.__origin__ is list or model.__origin__ is dict
        ):
            inner_type = model.__args__[0]
            if hasattr(inner_type, "__name__") and inner_type.__name__ in models:
                graph[model_name].add(sanitize_name(inner_type.__name__))
        else:
            logging.warning(
                f"Model '{model_name}' is not a Pydantic model, dict or list type"
            )

    # finally, add any models which have zero dependencies
    for model_name in models:
        if model_name not in graph:
            graph[model_name] = set()
    return graph


def handle_dependencies(models: Dict[str, Type[BaseModel]]):
    graph = build_dependency_graph(models)
    sorted_models = topological_sort(graph)
    circular_models = detect_circular_dependencies(graph)
    break_circular_dependencies(models, circular_models)
    return graph, circular_models, sorted_models


def topological_sort(graph: Dict[str, Set[str]]) -> List[str]:
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
        model = queue.pop(
            0
        )  # Use pop(0) instead of popleft() for deterministic behavior
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
        logging.warning(
            f"Circular dependencies detected among models: {missing_models}"
        )
        sorted_models.extend(missing_models)

    return sorted_models


def detect_circular_dependencies(graph: Dict[str, Set[str]]) -> Set[str]:
    circular_models = set()
    visited = set()
    stack = set()

    # Use a copy of the graph's keys to avoid modifying the dictionary during iteration
    def visit(model: str):
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

def replace_circular_references(annotation: Any, circular_models: Set[str]) -> Any:
    """Recursively replace circular model references in annotations with ForwardRef."""
    origin = get_origin(annotation)
    args = get_args(annotation)

    if not args:
        # Base case: simple type, check if it's circular
        if isinstance(annotation, type) and annotation.__name__ in circular_models:
            return ForwardRef(annotation.__name__)
        return annotation

    # Recurse into generic types
    new_args = tuple(replace_circular_references(arg, circular_models) for arg in args)
    return origin[new_args] if origin else annotation

def break_circular_dependencies(
    models: Dict[str, Type[BaseModel]], circular_models: Set[str]
):
    """Replace circular references in models with ForwardRef."""
    for model_name in circular_models:
        model = models[model_name]
        for field_name, field in model.model_fields.items():
            # Modify field.annotation directly
            field.annotation = replace_circular_references(field.annotation, circular_models)

# def break_circular_dependencies(
#     models: Dict[str, Type[BaseModel]], circular_models: Set[str]
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
def load_specs(folder_path: str) -> List[Dict[str, Any]]:
    return [
        json.load(open(os.path.join(folder_path, f)))
        for f in os.listdir(folder_path)
        if f.endswith(".json")
    ]


def get_api_name(spec: Dict[str, Any]) -> str:
    return spec["info"]["title"]


# Combine components and paths from all OpenAPI specs
def combine_components_and_paths(
    specs: List[Dict[str, Any]], pydantic_names: Dict[str, str]
) -> tuple[Dict[str, Any], Dict[str, Any]]:
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


def are_models_equal(model1: Type[BaseModel], model2: Type[BaseModel]) -> bool:
    """Check if two Pydantic models are equal based on their fields, types, and metadata."""
    # Compare field structure
    if set(model1.model_fields.keys()) != set(model2.model_fields.keys()):
        return False

    # Compare each field's annotation, alias, default, and constraints
    for field_name in model1.model_fields.keys():
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
        if hasattr(field1, 'json_schema_extra') and hasattr(field2, 'json_schema_extra') and field1.json_schema_extra != field2.json_schema_extra:
            return False

    return True


def deduplicate_models(
    models: Dict[str, Union[Type[BaseModel], Type[List]]],
) -> Dict[str, Union[Type[BaseModel], Type[List]]]:
    """Deduplicate models by removing models with the same content."""
    deduplicated_models = {}
    reference_map = {}

    # Compare models to detect duplicates
    for model_name, model in models.items():
        found_duplicate = False

        # Compare with already deduplicated models
        for dedup_model_name, dedup_model in deduplicated_models.items():
            if isinstance(model, type) and isinstance(dedup_model, type) and are_models_equal(model, dedup_model):
                reference_map[model_name] = dedup_model_name
                found_duplicate = True
                logging.info(
                    f"Model '{model_name}' is a duplicate of '{dedup_model_name}'"
                )
                break

            # Handle List models separately by comparing their inner types
            model_origin = get_origin(model)
            dedup_model_origin = get_origin(dedup_model)

            if model_origin in {list, List} and dedup_model_origin in {list, List}:
                model_inner_type = get_args(model)[0]
                dedup_inner_type = get_args(dedup_model)[0]

                # If the inner types of the lists are the same, consider them duplicates
                if model_inner_type == dedup_inner_type:
                    reference_map[model_name] = dedup_model_name
                    found_duplicate = True
                    logging.info(
                        f"Model '{model_name}' is a duplicate of '{dedup_model_name}'"
                    )
                    break

        # If no duplicate found, keep the model
        if not found_duplicate:
            deduplicated_models[model_name] = model

    # Return the deduplicated models and reference map
    return deduplicated_models, reference_map


def update_model_references(
    models: Dict[str, Union[Type[BaseModel], Type[List]]], reference_map: Dict[str, str]
) -> Dict[str, Union[Type[BaseModel], Type[List]]]:
    """Update references in models based on the deduplication reference map, including nested generics."""

    def resolve_model_reference(annotation: Any) -> Any:
        """Resolve references in the model recursively, including nested types."""
        origin = get_origin(annotation)
        args = get_args(annotation)

        # Handle Union, List, or any other generic types
        if origin in {Union, list, List, Optional} and args:
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


def create_config(spec: Dict[str, Any], output_path: str, base_url: str) -> None:
    class_name = f"{sanitize_name(get_api_name(spec))}Client"
    paths = spec.get("paths", {})

    config_lines = []
    api_path = "/" + spec.get("servers", [{}])[0].get("url", "").split("/", 3)[3]
    config_lines.append(f'base_url = "{base_url}"\n')
    config_lines.append("endpoints = {\n")

    for path, methods in paths.items():
        for method, details in methods.items():
            operation_id = details.get("operationId")
            if operation_id:
                path_uri = join_url_paths(api_path, path)
                path_params = [
                    param["name"]
                    for param in details.get("parameters", [])
                    if param["in"] == "path"
                ]
                for i, param in enumerate(path_params):
                    path_uri = path_uri.replace(f"{{{param}}}", f"{{{i}}}")

                response_content = details["responses"].get("200", {})

                model_name = get_model_name_from_path(response_content)

                config_lines.append(
                    f"    '{operation_id}': {{'uri': '{path_uri}', 'model': '{model_name}'}},\n"
                )

    config_lines.append("}\n")

    config_file_path = os.path.join(output_path, f"{class_name}_config.py")
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)

    with open(config_file_path, "w") as config_file:
        config_file.writelines(config_lines)

    logging.info(f"Config file generated at: {config_file_path}")


def classify_parameters(
    parameters: List[Dict[str, Any]],
) -> Tuple[List[str], List[str]]:
    """Classify parameters into path and query parameters."""
    path_params = [param["name"] for param in parameters if param["in"] == "path"]
    query_params = [param["name"] for param in parameters if param["in"] == "query"]
    return path_params, query_params


def create_class(spec: Dict[str, Any], output_path: str) -> None:
    paths = spec.get("paths", {})
    class_name = f"{sanitize_name(get_api_name(spec))}Client"

    class_lines = []
    class_lines.append(f"from .{class_name}_config import endpoints, base_url\n")
    class_lines.append("from ..core import ApiError, ResponseModel, Client\n")
    path_lines = [f"class {class_name}(Client):\n"]

    all_types = set()
    all_package_models = set()
    api_path = "/" + spec.get("servers", [{}])[0].get("url", "").split("/", 3)[3]

    for path, methods in paths.items():
        full_path = join_url_paths(api_path, path)
        for method, details in methods.items():
            operation_id = details.get("operationId")
            if operation_id:
                parameters = details.get("parameters", [])
                all_types.update(
                    [map_openapi_type(param["schema"]["type"]) for param in parameters]
                )

                param_str = create_function_parameters(parameters)
                response_content = details["responses"].get("200", {})

                model_name = get_model_name_from_path(response_content)
                all_package_models.add(model_name)

                # Sanitize the operation_id to ensure it's a valid Python identifier
                sanitized_operation_id = sanitize_name(operation_id, prefix="Query")
                path_lines.append(
                    f"    def {sanitized_operation_id}(self, {param_str}) -> ResponseModel[{model_name}] | ApiError:\n"
                )

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
                path_lines.append(
                    f"        '''\n        {docstring}\n\n  Parameters:\n{docstring_parameters}\n        '''\n"
                )

                path_params, query_params = classify_parameters(parameters)

                formatted_path_params = ", ".join(
                    [sanitize_field_name(param) for param in path_params]
                )
                formatted_query_params = ", ".join(
                    [
                        f"'{param}': {sanitize_field_name(param)}"
                        for param in query_params
                    ]
                )

                if formatted_query_params:
                    query_params_dict = f"endpoint_args={{ {formatted_query_params} }}"
                else:
                    query_params_dict = "endpoint_args=None"

                if path_params:
                    path_lines.append(
                        f"        return self._send_request_and_deserialize(base_url, endpoints['{operation_id}'], params=[{formatted_path_params}], {query_params_dict})\n\n"
                    )
                else:
                    path_lines.append(
                        f"        return self._send_request_and_deserialize(base_url, endpoints['{operation_id}'], {query_params_dict})\n\n"
                    )

    valid_type_imports = all_types - get_builtin_types()
    valid_type_import_strings = sorted([t.__name__ for t in valid_type_imports])
    if valid_type_import_strings:
        class_lines.append(
            f"from typing import {', '.join(valid_type_import_strings)}\n"
        )
    if all_package_models:
        class_lines.append(
            f"from ..models import {', '.join(sorted(all_package_models))}\n"
        )
    class_lines.append("\n")
    class_file_path = os.path.join(output_path, f"{class_name}.py")
    os.makedirs(os.path.dirname(class_file_path), exist_ok=True)
    with open(class_file_path, "w") as class_file:
        class_file.writelines(class_lines)
        class_file.writelines(path_lines)

    logging.info(f"Class file generated at: {class_file_path}")


def get_model_name_from_path(
    response_content: Dict[str, Any], only_arrays: bool = False
) -> str:
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


def create_function_parameters(parameters: List[Dict[str, Any]]) -> str:
    """Create a string of function parameters, ensuring they are safe Python identifiers."""
    # Sort parameters to ensure required ones come first
    sorted_parameters = sorted(
        parameters, key=lambda param: not param.get("required", False)
    )

    param_str = ", ".join(
        [
            f"{sanitize_field_name(param['name'])}: {map_openapi_type(param['schema']['type']).__name__} | None = None"
            if not param.get("required", False)
            else f"{sanitize_field_name(param['name'])}: {map_openapi_type(param['schema']['type']).__name__}"
            for param in sorted_parameters
        ]
    )
    return param_str


def save_classes(specs: List[Dict[str, Any]], base_path: str, base_url: str) -> None:
    """Create config and class files for each spec in the specs list."""

    class_names = [f"{sanitize_name(get_api_name(spec))}Client" for spec in specs]
    init_file_path = os.path.join(base_path, "__init__.py")
    with open(init_file_path, "w") as init_file:
        # init_file.write(f"# {init_file_path}\n")
        class_names_joined = ',\n    '.join(class_names)
        init_file.write(
            f"from .endpoints import (\n    {class_names_joined}\n)\n"
        )
        # init_file.write("\n".join([f"from .endpoints.{name} import {name}" for name in class_names]))
        # init_file.write("from ..core import Client\n")
        # init_file.write("from ..core import RestClient\n")
        init_file.write("from . import models\n")
        # init_file.write("from .models import ApiError, GenericResponseModel, ResponseModel\n")
        # other_classes = ["Client", "RestClient", "ApiError", "GenericResponseModel", "ResponseModel"]
        init_file.write("__all__ = [\n")
        init_file.write(",\n".join([f"    '{name}'" for name in class_names]))
        # init_file.write(",\n".join([f"    '{name}'" for name in other_classes]))
        init_file.write(",\n    'models'\n]\n")

    endpoint_path = os.path.join(base_path, "endpoints")
    os.makedirs(endpoint_path, exist_ok=True)
    endpoint_init_file = os.path.join(endpoint_path, "__init__.py")
    with open(endpoint_init_file, "w") as endpoint_init:
        # endpoint_init.write(f"# {endpoint_init_file}\n")
        endpoint_init.write(
            "\n".join([f"from .{name} import {name}" for name in class_names])
        )
        endpoint_init.write("\n__all__ = [\n")
        endpoint_init.write(",\n".join([f"    '{name}'" for name in class_names]))
        endpoint_init.write("\n]\n")

    for spec in specs:
        api_name = get_api_name(spec)
        logging.info(f"Creating config and class files for {api_name}...")

        create_config(spec, endpoint_path, base_url)
        create_class(spec, endpoint_path)

    logging.info("All classes and configs saved.")


def map_deduplicated_name(type_name: str, reference_map: Dict[str, str]) -> str:
    if type_name in reference_map:
        return reference_map[type_name]
    return type_name


def _create_schema_name_mapping(combined_components: Dict[str, Any]) -> Dict[str, str]:
    """Create reverse mapping from sanitized names back to original schema names."""
    schema_name_mapping = {}
    for schema_name in combined_components.keys():
        sanitized = sanitize_name(schema_name)
        schema_name_mapping[sanitized] = schema_name
    return schema_name_mapping


def _update_schema_with_reference_map(
    schema_name: str,
    schema: Dict[str, Any],
    reference_map: Dict[str, str],
    schema_name_mapping: Dict[str, str],
    combined_components: Dict[str, Any],
) -> Tuple[str, Dict[str, Any]]:
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
    spec: Dict[str, Any],
    combined_components: Dict[str, Any],
    reference_map: Dict[str, str],
    schema_name_mapping: Dict[str, str],
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


def _update_reference_in_schema(schema: Dict[str, Any], reference_map: Dict[str, str]) -> None:
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


def _update_paths_in_spec(spec: Dict[str, Any], reference_map: Dict[str, str]) -> None:
    """Update all path references in a spec using the reference map."""
    if "paths" in spec:
        for path in spec["paths"].values():
            for method in path.values():
                if "responses" in method:
                    for response in method["responses"].values():
                        if (
                            "content" in response
                            and "application/json" in response["content"]
                        ):
                            schema = response["content"]["application/json"].get("schema", {})
                            _update_reference_in_schema(schema, reference_map)


def update_specs_with_model_changes(
    specs: List[Dict[str, Any]],
    combined_components: Dict[str, Any],
    reference_map: Dict[str, str],
) -> List[Dict[str, Any]]:
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


def _load_and_process_specs(spec_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
    """Load OpenAPI specs and process components and paths."""
    logging.info("Loading OpenAPI specs...")
    specs = load_specs(spec_path)
    if not specs:
        raise ValueError(f"No valid specifications found in {spec_path}")

    logging.info("Generating components...")
    pydantic_names = {}
    combined_components, combined_paths = combine_components_and_paths(
        specs, pydantic_names
    )

    logging.info("Creating array types from model paths...")
    # some paths have an array type as a response, we need to handle these separately
    array_types = create_array_types_from_model_paths(
        combined_paths, combined_components
    )
    combined_components.update(array_types)

    return specs, combined_components, combined_paths


def _generate_and_process_models(combined_components: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Generate Pydantic models and process them for deduplication."""
    logging.info("Generating Pydantic models...")
    models = {}
    create_pydantic_models(combined_components, models)

    logging.info("Creating generic response model...")
    generic_model = create_generic_response_model()
    models["GenericResponseModel"] = generic_model

    # Deduplicate models before saving them
    logging.info("Deduplicating models...")
    deduplicated_models, reference_map = deduplicate_models(models)

    # Update model references
    models = update_model_references(deduplicated_models, reference_map)

    return models, reference_map


def _handle_dependencies_and_save_models(models: Dict[str, Any], output_path: str) -> Tuple[Dict[str, List[str]], List[str], List[str]]:
    """Handle model dependencies and save models to files."""
    logging.info("Handling dependencies...")
    dependency_graph, circular_models, sorted_models = handle_dependencies(models)

    # Now save the deduplicated models
    logging.info("Saving models to files...")
    save_models(models, output_path, dependency_graph, circular_models, sorted_models)

    return dependency_graph, circular_models, sorted_models


def _generate_classes_and_diagrams(
    specs: List[Dict[str, Any]],
    combined_components: Dict[str, Any],
    reference_map: Dict[str, str],
    output_path: str,
    dependency_graph: Dict[str, List[str]],
    sorted_models: List[str],
) -> None:
    """Generate API classes and create documentation diagrams."""
    # Create config and class
    logging.info("Creating config and class files...")
    base_url = "https://api.tfl.gov.uk"
    logging.info("Updating specs with model changes...")
    updated_specs = update_specs_with_model_changes(
        specs, combined_components, reference_map
    )

    save_classes(updated_specs, output_path, base_url)

    logging.info("Creating Mermaid class diagram...")
    create_mermaid_class_diagram(
        dependency_graph, sorted_models, os.path.join(output_path, "class_diagram.mmd")
    )


def main(spec_path: str, output_path: str):
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
        specs, combined_components, combined_paths = _load_and_process_specs(spec_path)
        models, reference_map = _generate_and_process_models(combined_components)
        dependency_graph, circular_models, sorted_models = _handle_dependencies_and_save_models(models, output_path)
        _generate_classes_and_diagrams(specs, combined_components, reference_map, output_path, dependency_graph, sorted_models)

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
    parser = argparse.ArgumentParser(
        description="Process OpenAPI spec and generate output."
    )
    parser.add_argument("specpath", help="Path to the OpenAPI specification file")
    parser.add_argument("output", help="Path to the output file")

    args = parser.parse_args()

    main(args.specpath, args.output)
