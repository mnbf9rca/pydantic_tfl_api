"""FileManager class that handles all file I/O operations for the build system."""

import ast
import glob
import keyword
import logging
import os
import re
import shutil
import types
from enum import Enum
from io import TextIOWrapper
from pathlib import Path
from typing import Any, ForwardRef, Union, get_args, get_origin
from typing import __all__ as typing_all

from pydantic import BaseModel, RootModel
from pydantic.fields import FieldInfo

from .utilities import (
    escape_description_for_field,
    extract_inner_types,
    get_builtin_types,
    normalize_description,
    sanitize_field_name,
    sanitize_name,
)


class FileManager:
    """Handles all file I/O operations for the build system."""

    def __init__(self) -> None:
        """Initialize the FileManager with empty state."""
        self._generated_files: list[str] = []
        self.logger = logging.getLogger(__name__)

    def save_models(
        self,
        models: dict[str, type[BaseModel] | type[list]],
        base_path: str,
        dependency_graph: dict[str, set[str]],
        circular_models: set[str],
        sorted_models: list[str] | None = None,
        model_descriptions: dict[str, str] | None = None,
        field_descriptions: dict[str, dict[str, str]] | None = None,
    ) -> None:
        """
        Save models to individual files and create the __init__.py file.

        Args:
            models: Dictionary of model names to model classes
            base_path: Base directory path where models will be saved
            dependency_graph: Model dependency relationships
            circular_models: Set of models with circular dependencies
            sorted_models: Optional list of models in dependency order
            model_descriptions: Optional dictionary of model-level descriptions from OpenAPI
            field_descriptions: Optional dictionary of field-level descriptions per model
        """
        # Provide defaults if not specified
        if model_descriptions is None:
            model_descriptions = {}
        if field_descriptions is None:
            field_descriptions = {}
        models_dir = os.path.join(base_path, "models")
        os.makedirs(models_dir, exist_ok=True)

        # Track the models directory creation
        self._generated_files.append(models_dir)

        init_file = os.path.join(models_dir, "__init__.py")
        self._generated_files.append(init_file)

        with open(init_file, "w") as init_f:
            # Standard library imports first
            init_f.write("from typing import Literal\n\n")

            # Write import statements in dependency-aware order to minimize forward references
            self.write_import_statements(init_f, models, models_dir, sorted_models)

            # Import GenericResponseModel from core for backward compatibility
            init_f.write("\nfrom ..core.package_models import GenericResponseModel\n")

            for model_name, model in models.items():
                self.save_model_file(
                    model_name,
                    model,
                    models,
                    models_dir,
                    dependency_graph,
                    circular_models,
                    init_f,
                    model_descriptions,
                    field_descriptions,
                )

            # Add ResponseModelName Literal type
            # Include GenericResponseModel in the Literal since it's a valid response model
            model_names_for_literal = ",\n    ".join(f'"{key}"' for key in sorted(models.keys()))
            init_f.write(
                f'\nResponseModelName = Literal[\n    {model_names_for_literal},\n    "GenericResponseModel"\n]\n\n'
            )

            model_names = ",\n    ".join(f'"{key}"' for key in sorted(models.keys()))
            init_f.write(f"__all__ = [\n    {model_names},\n    'GenericResponseModel'\n]\n")

        # Write enums after saving the models
        self._write_enum_files(models, models_dir)

    def save_model_file(
        self,
        model_name: str,
        model: Any,
        models: dict[str, type[BaseModel]],
        models_dir: str,
        dependency_graph: dict[str, set[str]],
        circular_models: set[str],
        init_f: TextIOWrapper,
        model_descriptions: dict[str, str],
        field_descriptions: dict[str, dict[str, str]],
    ) -> None:
        """
        Save an individual model to its own file.

        Args:
            model_name: Name of the model
            model: The model class or type
            models: Dictionary of all models
            models_dir: Directory where models are saved
            dependency_graph: Model dependency relationships
            circular_models: Set of models with circular dependencies
            init_f: File handle for the __init__.py file
            model_descriptions: Dictionary of model-level descriptions from OpenAPI
            field_descriptions: Dictionary of field-level descriptions per model
        """
        sanitized_model_name = sanitize_name(model_name)
        model_file = os.path.join(models_dir, f"{sanitized_model_name}.py")
        os.makedirs(models_dir, exist_ok=True)

        # Track the generated file
        self._generated_files.append(model_file)

        # Files will be overwritten directly - git serves as our backup
        with open(model_file, "w") as mf:
            if self._is_enum_model(model):
                self._handle_enum_model(mf, model, sanitized_model_name)
            elif self._is_list_or_dict_model(model):
                self._handle_list_or_dict_model(
                    mf,
                    model,
                    models,
                    dependency_graph,
                    circular_models,
                    sanitized_model_name,
                )
            else:
                self._handle_regular_model(
                    mf,
                    model,
                    models,
                    dependency_graph,
                    circular_models,
                    sanitized_model_name,
                    model_descriptions,
                    field_descriptions,
                )

    def get_pydantic_imports(self, sanitized_model_name: str, is_root_model: bool) -> str:
        """
        Get the appropriate pydantic imports based on model type and name.

        Args:
            sanitized_model_name: Sanitized name of the model
            is_root_model: Whether this is a RootModel or BaseModel

        Returns:
            Import statement string for pydantic components (alphabetically sorted)
        """
        # Build imports list and sort alphabetically for ruff/isort compliance
        imports = ["ConfigDict", "RootModel"] if is_root_model else ["BaseModel", "ConfigDict", "Field"]
        return f"from pydantic import {', '.join(imports)}"

    def get_model_config(self, sanitized_model_name: str) -> str:
        """
        Get the appropriate model_config for the model.

        Args:
            sanitized_model_name: Sanitized name of the model

        Returns:
            Model configuration string
        """
        return "model_config = ConfigDict(from_attributes=True)"

    def write_import_statements(
        self,
        init_f: TextIOWrapper,
        models: dict[str, type[BaseModel]],
        models_dir: str,
        sorted_models: list[str] | None = None,
    ) -> None:
        """
        Write import statements in dependency-aware order to minimize forward references.

        Args:
            init_f: File handle for the __init__.py file
            models: Dictionary of all models
            models_dir: Directory where models are saved
            sorted_models: Optional list of models in dependency order
        """
        # If we have a topologically sorted order, use it; otherwise fall back to alphabetical
        model_order = sorted_models or sorted(models.keys())

        # Write imports in dependency order to minimize forward references
        for model_name in model_order:
            if model_name in models:
                init_f.write(f"from .{model_name} import {model_name}\n")

    def sanitize_field_name(self, field_name: str) -> str:
        """
        Sanitize field names that are Python reserved keywords.

        Args:
            field_name: The field name to sanitize

        Returns:
            Sanitized field name with _field suffix if needed
        """
        if keyword.iskeyword(field_name):
            logging.info(f"Field name '{field_name}' is a Python keyword, sanitizing to '{field_name}_field'")
        return f"{field_name}_field" if keyword.iskeyword(field_name) else field_name

    def get_generated_files(self) -> list[str]:
        """
        Get list of all generated files tracked by this FileManager.

        Returns:
            List of generated file paths
        """
        return self._generated_files.copy()

    def clear_generated_files(self) -> None:
        """Clear the list of generated files."""
        self._generated_files.clear()

    # Private helper methods

    def _is_enum_model(self, model: Any) -> bool:
        """Determine if the model is an enum type."""
        return isinstance(model, type) and issubclass(model, Enum)

    def _is_list_or_dict_model(self, model: Any) -> str | None:
        """Determine if the model is a list or dict type and return the type string ('list' or 'dict')."""
        origin = get_origin(model)
        if origin is list:
            return "list"
        return "dict" if origin is dict else None

    def _validate_list_dict_args(self, model_type: str, args: tuple) -> None:
        """Validate argument counts for list/dict models."""
        if model_type == "list" and len(args) != 1:
            raise ValueError(f"list type should have exactly 1 argument, got {len(args)}")
        elif model_type == "dict" and len(args) != 2:
            raise ValueError(f"dict type should have exactly 2 arguments (key, value), got {len(args)}")

    def _extract_list_dict_types(self, model_type: str, args: tuple) -> tuple[Any, Any | None, Any]:
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

    def _collect_type_imports(
        self, type_obj: Any, models: dict[str, type[BaseModel]], typing_imports: set[str], module_imports: set[str]
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

    def _generate_list_dict_class_definition(
        self, model_type: str, sanitized_model_name: str, type_names: dict[str, str]
    ) -> str:
        """Generate class definition for list/dict models."""
        if model_type == "list":
            return f"class {sanitized_model_name}(RootModel[list[{type_names['inner']}]]):\n"
        elif model_type == "dict":
            return f"class {sanitized_model_name}(RootModel[dict[{type_names['key']}, {type_names['value']}]]):\n"
        else:
            raise ValueError("Model is not a list or dict model.")

    def _write_imports_and_class(
        self,
        model_file: TextIOWrapper,
        typing_imports: set[str],
        module_imports: set[str],
        class_definition: str,
        sanitized_model_name: str,
    ) -> None:
        """Write all imports and class definition to the model file."""
        # Write imports in proper order following ruff/isort standards:
        # 1. Standard library imports (from typing)
        # 2. Third-party imports (from pydantic)
        # 3. Local/first-party imports (from .)

        import_lines = []

        # Write typing imports (standard library) first
        if typing_imports:
            clean_typing_imports = sorted(typing_imports - get_builtin_types())
            if clean_typing_imports:
                import_lines.append(f"from typing import {', '.join(sorted(clean_typing_imports))}")

        # Write pydantic imports (third-party)
        if import_lines:
            import_lines.append("")  # Blank line between groups
        import_lines.append(self.get_pydantic_imports(sanitized_model_name, is_root_model=True))

        # Write module imports (local/relative imports)
        if module_imports:
            if import_lines:
                import_lines.append("")  # Blank line between groups
            import_lines.extend(sorted(module_imports))

        # Write all imports
        if import_lines:
            model_file.write("\n".join(import_lines) + "\n")

        # Write class definition
        model_file.write(f"\n\n{class_definition}")

        # Write model config
        model_file.write(f"\n    {self.get_model_config(sanitized_model_name)}\n")

    def _handle_list_or_dict_model(
        self,
        model_file: TextIOWrapper,
        model: Any,
        models: dict[str, type[BaseModel]],
        dependency_graph: dict[str, set[str]],
        circular_models: set[str],
        sanitized_model_name: str,
    ) -> None:
        """Handle models that are either list or dict types."""
        # Check if the model is a List or Dict
        model_type = self._is_list_or_dict_model(model)
        args = model.__args__

        # Validate and extract types using helper functions
        self._validate_list_dict_args(model_type, args)
        inner_type, key_type, value_type = self._extract_list_dict_types(model_type, args)

        # Collect imports
        # For modern Python, we don't need to import List/Dict anymore
        typing_imports: set[str] = set()
        module_imports: set[str] = set()

        # Handle imports and get type names
        type_names = {}
        if model_type == "list":
            type_names["inner"] = self._collect_type_imports(inner_type, models, typing_imports, module_imports)
        elif model_type == "dict":
            type_names["key"] = self._collect_type_imports(key_type, models, typing_imports, module_imports)
            type_names["value"] = self._collect_type_imports(value_type, models, typing_imports, module_imports)

        # Generate and write class using helper functions
        class_definition = self._generate_list_dict_class_definition(model_type, sanitized_model_name, type_names)
        self._write_imports_and_class(
            model_file, typing_imports, module_imports, class_definition, sanitized_model_name
        )

    def _handle_enum_model(
        self,
        model_file: TextIOWrapper,
        model: type[Enum],
        sanitized_model_name: str,
    ) -> None:
        """Handle enum models."""
        model_file.write("from enum import Enum\n\n\n")
        model_file.write(f"class {sanitized_model_name}(Enum):\n")
        for enum_member in model:
            model_file.write(f"    {enum_member.name} = '{enum_member.value}'\n")

    def _handle_regular_model(
        self,
        model_file: TextIOWrapper,
        model: BaseModel,
        models: dict[str, type[BaseModel]],
        dependency_graph: dict[str, set],
        circular_models: set[str],
        sanitized_model_name: str,
        model_descriptions: dict[str, str],
        field_descriptions: dict[str, dict[str, str]],
    ) -> None:
        """Handle regular BaseModel or RootModel types."""
        # Check if the model is a RootModel
        is_root_model = isinstance(model, type) and issubclass(model, RootModel)

        # Only process typing imports if the model has model_fields (i.e., it's a pydantic model)
        typing_imports = []
        if hasattr(model, "model_fields"):
            typing_imports = sorted(
                self._determine_typing_imports(model.model_fields, models, circular_models) - get_builtin_types()
            )

        import_set = set()

        # Add typing imports only if there are any
        if typing_imports:
            import_set.add(f"from typing import {', '.join(typing_imports)}")

        # Add pydantic imports using helper function
        import_set.add(self.get_pydantic_imports(sanitized_model_name, is_root_model))

        # Write imports for referenced models
        referenced_models = dependency_graph.get(sanitized_model_name, set())
        for ref_model in referenced_models:
            if ref_model != sanitized_model_name and ref_model not in {
                "Optional",
                "list",
                "Union",
            }:
                import_set.add(f"from .{ref_model} import {ref_model}")

        # Add Enum imports only if model has model_fields
        if hasattr(model, "model_fields"):
            import_set.update(self._find_enum_imports(model))

        # Write imports in proper order following ruff/isort standards:
        # 1. Standard library imports (from typing)
        # 2. Third-party imports (from pydantic)
        # 3. Local/first-party imports (from .)
        typing_imports = sorted([imp for imp in import_set if imp.startswith("from typing")])
        pydantic_imports = sorted([imp for imp in import_set if imp.startswith("from pydantic")])
        relative_imports = sorted([imp for imp in import_set if imp.startswith("from .")])

        # Build the import block with proper spacing
        all_imports = []
        if typing_imports:
            all_imports.extend(typing_imports)
        if pydantic_imports:
            if all_imports:
                all_imports.append("")  # Blank line between groups
            all_imports.extend(pydantic_imports)
        if relative_imports:
            if all_imports:
                all_imports.append("")  # Blank line between groups
            all_imports.extend(relative_imports)

        if all_imports:
            model_file.write("\n".join(all_imports) + "\n\n\n")

        # Write class definition
        if is_root_model:
            # Get the root annotation for RootModel
            if hasattr(model, "model_fields") and "root" in model.model_fields:
                root_annotation = model.model_fields["root"].annotation
                type_str = self._get_type_str(root_annotation, models)
                model_file.write(f"class {sanitized_model_name}(RootModel[{type_str}]):\n")
            else:
                # Fallback for RootModel without proper root field
                model_file.write(f"class {sanitized_model_name}(RootModel[list]):\n")
            # Add docstring if available (normalize and skip if empty)
            if sanitized_model_name in model_descriptions:
                desc = normalize_description(model_descriptions[sanitized_model_name])
                if desc:
                    model_file.write(f'    """{desc}"""\n\n')
        else:
            model_file.write(f"class {sanitized_model_name}(BaseModel):\n")
            # Add docstring if available (normalize and skip if empty)
            if sanitized_model_name in model_descriptions:
                desc = normalize_description(model_descriptions[sanitized_model_name])
                if desc:
                    model_file.write(f'    """{desc}"""\n\n')
            if hasattr(model, "model_fields"):
                self._write_model_fields(
                    model_file, model, models, circular_models, field_descriptions.get(sanitized_model_name, {})
                )

        # Pydantic model config
        model_file.write(f"\n    {self.get_model_config(sanitized_model_name)}\n")

        # Note: __slots__ removed - Pydantic v2 BaseModel already uses __slots__ internally
        # Manual __slots__ definition conflicts with Pydantic's metaclass

        # Add model_rebuild() if circular dependencies exist
        if sanitized_model_name in circular_models:
            model_file.write(f"\n{sanitized_model_name}.model_rebuild()\n")

    def _find_enum_imports(self, model: BaseModel) -> set[str]:
        """Find all enum imports in the model fields."""
        import_set = set()
        for _field_name, field in model.model_fields.items():
            inner_types = extract_inner_types(field.annotation)
            for inner_type in inner_types:
                if isinstance(inner_type, type) and issubclass(inner_type, Enum):
                    import_set.add(f"from .{inner_type.__name__} import {inner_type.__name__}")
        return import_set

    def _resolve_forward_refs_in_annotation(
        self, annotation: Any, models: dict[str, type[BaseModel]], circular_models: set[str]
    ) -> str:
        """
        Recursively resolve ForwardRef in an annotation to a string representation,
        handling Optional, List, and other generics, and quoting forward references.
        """

        origin = get_origin(annotation)
        args = get_args(annotation)

        # Handle Python 3.10+ union types (X | Y syntax) first
        if isinstance(annotation, types.UnionType):
            union_args = annotation.__args__
            if len(union_args) == 2 and type(None) in union_args:
                # It's an Optional type (X | None)
                non_none_arg = union_args[0] if union_args[0] is not type(None) else union_args[1]
                resolved_inner = self._resolve_forward_refs_in_annotation(non_none_arg, models, circular_models)
                return f"{resolved_inner} | None"
            else:
                # General union type (X | Y | Z)
                resolved_types = [
                    self._resolve_forward_refs_in_annotation(arg, models, circular_models) for arg in union_args
                ]
                return " | ".join(resolved_types)

        # Handle Optional as Union[T, NoneType] and convert it to T | None
        if origin is Union and len(args) == 2 and type(None) in args:
            non_none_arg = args[0] if args[0] is not type(None) else args[1]
            resolved_inner = self._resolve_forward_refs_in_annotation(non_none_arg, models, circular_models)
            return f"{resolved_inner} | None"

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
        resolved_args = ", ".join(
            self._resolve_forward_refs_in_annotation(arg, models, circular_models) for arg in args
        )
        return f"{origin.__name__}[{resolved_args}]"

    def _write_model_fields(
        self,
        model_file: TextIOWrapper,
        model: BaseModel,
        models: dict[str, type[BaseModel]],
        circular_models: set[str],
        field_descs: dict[str, str],
    ) -> list[str]:
        """Write the fields for the model and return the list of field names for __slots__."""
        field_names = []
        for field_name, field in model.model_fields.items():
            sanitized_field_name = sanitize_field_name(field_name)
            field_names.append(sanitized_field_name)

            # Resolve the field's annotation to get the type string, including handling ForwardRefs
            field_type = self._resolve_forward_refs_in_annotation(field.annotation, models, circular_models)

            # Determine field default value based on required status
            field_default = "..." if field.is_required() else "None"

            # For non-required fields, make the type optional (union with None)
            if not field.is_required() and not field_type.endswith(" | None") and field_type != "None":
                field_type = f"{field_type} | None"

            # Prepare description for Field() if available (escape and skip if empty)
            description_param = ""
            if sanitized_field_name in field_descs:
                escaped_desc = escape_description_for_field(field_descs[sanitized_field_name])
                if escaped_desc:  # Only add if not empty after normalization
                    description_param = f', description="{escaped_desc}"'

            # Build Field() call with alias and/or description
            field_params = field_default
            if field.alias and field.alias != field_name:
                field_params += f", alias='{field.alias}'"
            field_params += description_param

            model_file.write(f"    {sanitized_field_name}: {field_type} = Field({field_params})\n")

        return field_names

    def _write_enum_files(self, models: dict[str, type[BaseModel]], models_dir: str) -> None:
        """Write enum files directly from the model's fields."""
        for model in models.values():
            if hasattr(model, "model_fields"):
                for field in model.model_fields.values():
                    inner_types = extract_inner_types(field.annotation)
                    for inner_type in inner_types:
                        if isinstance(inner_type, type) and issubclass(inner_type, Enum):
                            enum_name = inner_type.__name__
                            enum_file = os.path.join(models_dir, f"{enum_name}.py")

                            # Track the generated enum file
                            self._generated_files.append(enum_file)

                            os.makedirs(models_dir, exist_ok=True)
                            with open(enum_file, "w") as ef:
                                ef.write("from enum import Enum\n\n\n")
                                ef.write(f"class {enum_name}(Enum):\n")
                                for enum_member in inner_type:
                                    ef.write(f"    {enum_member.name} = '{enum_member.value}'\n")

    def _get_type_str(self, annotation: Any, models: dict[str, type[BaseModel]]) -> str:
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
                return f"{self._get_type_str(non_none_arg, models)} | None"
            else:
                # General union type (X | Y | Z)
                inner_types = " | ".join(self._get_type_str(arg, models) for arg in args)
                return inner_types

        elif hasattr(annotation, "__origin__"):
            origin = annotation.__origin__
            args = annotation.__args__

            # Handle list (e.g., list[str], list[Casualty])
            if origin is list:
                inner_type = self._get_type_str(args[0], models)
                return f"list[{inner_type}]"

            # Handle dict (e.g., dict[str, int])
            elif origin is dict:
                key_type = self._get_type_str(args[0], models)
                value_type = self._get_type_str(args[1], models)
                return f"dict[{key_type}, {value_type}]"

            # Handle Optional and Union (e.g., Optional[int], Union[str, int])
            elif origin is Union:
                if len(args) == 2 and type(None) in args:
                    # It's an Optional type - convert to X | None format
                    non_none_arg = args[0] if args[0] is not type(None) else args[1]
                    return f"{self._get_type_str(non_none_arg, models)} | None"
                else:
                    # General Union type
                    inner_types = ", ".join(self._get_type_str(arg, models) for arg in args)
                    return f"Union[{inner_types}]"

        elif hasattr(annotation, "__name__") and annotation.__name__ in models:
            # Handle references to other models (e.g., Casualty)
            return annotation.__name__

        return "Any"

    def _determine_typing_imports(
        self,
        model_fields: dict[str, FieldInfo],
        models: dict[str, type[BaseModel] | type],
        circular_models: set[str],
    ) -> set[str]:
        """Determine necessary typing imports based on the field annotations."""
        import_set = set()

        for field in model_fields.values():
            field_annotation = self._get_type_str(field.annotation, models)

            # Check for any type in typing.__all__
            # Use word boundaries to avoid false matches (e.g., "Type" in "PathAttribute")
            for type_name in typing_all:
                # Match only as standalone identifiers: preceded/followed by non-identifier chars
                # This prevents "Type" from matching within "PathAttribute"
                pattern = rf"\b{re.escape(type_name)}\b"
                if re.search(pattern, field_annotation):
                    import_set.add(type_name)

            # Check for circular references
            if field_annotation in circular_models:
                import_set.add("ForwardRef")

        return import_set

    def create_mermaid_class_diagram(
        self,
        dependency_graph: dict[str, set[str]],
        sort_order: list[str],
        output_file: str,
        endpoints_path: str | None = None,
    ) -> None:
        """Create a Mermaid class diagram from the dependency graph with optional API client relationships.

        Args:
            dependency_graph: Dictionary mapping model names to their dependencies
            sort_order: List of model names in topologically sorted order
            output_file: Path to output .mmd file
            endpoints_path: Optional path to endpoints directory for client->model relationships
        """
        # Extract client->model relationships if endpoints path is provided
        client_to_models: dict[str, set[str]] = {}
        if endpoints_path and os.path.exists(endpoints_path):
            client_to_models = self._extract_client_to_model_relationships(endpoints_path)

        with open(output_file, "w") as f:
            # Add config to hide empty member boxes for cleaner display
            f.write("---\n")
            f.write("config:\n")
            f.write("  class:\n")
            f.write("    hideEmptyMembersBox: true\n")
            f.write("---\n")
            f.write("classDiagram\n")

            # Write client declarations with annotation if we have client data
            if client_to_models:
                f.write("    %% API Clients\n")
                for client_name in sorted(client_to_models.keys()):
                    f.write(f"    class {client_name}{{\n")
                    f.write("        <<Client>>\n")
                    f.write("    }\n")
                f.write("\n")

                # Write client->model relationships (dotted arrows for "returns")
                f.write("    %% API Endpoint -> Response mappings (dotted)\n")
                for client_name in sorted(client_to_models.keys()):
                    for model_name in sorted(client_to_models[client_name]):
                        f.write(f"    {client_name} ..> {model_name} : returns\n")
                f.write("\n")

                # Write model->model dependencies (solid arrows for "contains")
                f.write("    %% Model -> Model dependencies (solid)\n")

            # Write model dependencies
            for model in sort_order:
                if model in dependency_graph:
                    dependencies = sorted(dependency_graph[model])
                    if dependencies:
                        for dep in dependencies:
                            f.write(f"    {model} --> {dep} : contains\n")
                    else:
                        f.write(f"    class {model}\n")
                else:
                    f.write(f"    class {model}\n")

        self.logger.info(f"Created Mermaid class diagram at: {output_file}")

    def create_mermaid_api_mindmap(self, endpoints_path: str, output_file: str) -> None:
        """Create a Mermaid mindmap showing API clients and their response types.

        This creates an explorable hierarchical view of the entire API surface,
        showing both client-to-models and model-to-clients relationships to reveal reuse.

        Args:
            endpoints_path: Path to endpoints directory containing client config files
            output_file: Path to output .mmd file
        """
        if not os.path.exists(endpoints_path):
            self.logger.warning(f"Endpoints path does not exist: {endpoints_path}")
            return

        client_to_models = self._extract_client_to_model_relationships(endpoints_path)

        # Build reverse mapping: model -> clients that use it
        model_to_clients: dict[str, set[str]] = {}
        for client_name, models in client_to_models.items():
            for model_name in models:
                if model_name not in model_to_clients:
                    model_to_clients[model_name] = set()
                model_to_clients[model_name].add(client_name)

        with open(output_file, "w") as f:
            f.write("mindmap\n")
            f.write("  root((TfL API))\n")

            # Show each client with its response models
            # Use shapes: hexagons for clients (services), rounded squares for models (data)
            for client_name in sorted(client_to_models.keys()):
                # Hexagon shape for API client services
                f.write(f"    {{{{{client_name}}}}}\n")
                for model_name in sorted(client_to_models[client_name]):
                    client_count = len(model_to_clients[model_name])
                    # Rounded square shape for response models
                    if client_count > 1:
                        # Format: "ModelName - used by N clients"
                        f.write(f"      ({model_name} - {client_count} clients)\n")
                    else:
                        f.write(f"      ({model_name})\n")

        self.logger.info(f"Created Mermaid API mindmap at: {output_file}")

    def _extract_client_to_model_relationships(self, endpoints_path: str) -> dict[str, set[str]]:
        """Extract client->model relationships from endpoint config files.

        Args:
            endpoints_path: Path to the endpoints directory containing *_config.py files

        Returns:
            Dictionary mapping client names to sets of model names they return
        """
        client_to_models: dict[str, set[str]] = {}

        # Find all *_config.py files in the endpoints directory
        config_files = glob.glob(os.path.join(endpoints_path, "*_config.py"))

        for config_file in config_files:
            try:
                # Extract client name from filename (e.g., "LineClient_config.py" -> "LineClient")
                client_name = os.path.basename(config_file).replace("_config.py", "")

                with open(config_file) as f:
                    content = f.read()
                    # Parse the Python file as AST to safely extract the endpoints dict
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        # Find the 'endpoints' variable assignment
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if (
                                    isinstance(target, ast.Name)
                                    and target.id == "endpoints"
                                    and isinstance(node.value, ast.Dict)
                                ):
                                    # Extract model names from the endpoints dict
                                    models = self._extract_models_from_dict_ast(node.value)
                                    if models:
                                        client_to_models[client_name] = models

            except Exception as e:
                self.logger.warning(f"Failed to parse config file {config_file}: {e}")
                continue

        return client_to_models

    def _extract_models_from_dict_ast(self, dict_node: ast.Dict) -> set[str]:
        """Extract model names from an AST Dict node representing the endpoints dictionary.

        Args:
            dict_node: AST Dict node from the endpoints assignment

        Returns:
            Set of model names found in the 'model' values
        """
        models: set[str] = set()

        for value in dict_node.values:
            # Each value should be a dict like {'uri': '...', 'model': 'ModelName'}
            if isinstance(value, ast.Dict):
                for i, key in enumerate(value.keys):
                    if isinstance(key, ast.Constant) and key.value == "model" and i < len(value.values):
                        # Extract the model name
                        model_value = value.values[i]
                        if isinstance(model_value, ast.Constant) and isinstance(model_value.value, str):
                            models.add(model_value.value)

        return models

    def copy_infrastructure(self, output_path: str) -> None:
        """Copy hand-crafted infrastructure components to the output directory.

        This function copies the core infrastructure files (client.py, package_models.py, etc.)
        from the infrastructure/core directory to the output directory, ensuring that
        generated code has access to the necessary infrastructure components.

        Args:
            output_path: Directory where infrastructure should be copied

        Raises:
            FileNotFoundError: If infrastructure directory doesn't exist
            PermissionError: If unable to copy files
        """
        # Get the directory containing this script (should be project root/scripts/build_system)
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        infrastructure_dir = project_root / "infrastructure" / "core"

        if not infrastructure_dir.exists():
            raise FileNotFoundError(f"Infrastructure directory not found: {infrastructure_dir}")

        output_core_dir = Path(output_path) / "core"

        self.logger.info(f"Copying infrastructure from {infrastructure_dir} to {output_core_dir}")

        # Create output core directory and copy all infrastructure files
        output_core_dir.mkdir(parents=True, exist_ok=True)

        for infrastructure_file in infrastructure_dir.glob("*.py"):
            destination = output_core_dir / infrastructure_file.name

            shutil.copy2(infrastructure_file, destination)
            self.logger.info(f"Copied infrastructure: {infrastructure_file.name}")
            self._generated_files.append(str(destination))
