"""FileManager class that handles all file I/O operations for the build system."""

import keyword
import logging
import os
import types
from enum import Enum
from io import TextIOWrapper
from typing import Any, ForwardRef, Union, get_args, get_origin
from typing import __all__ as typing_all

from pydantic import BaseModel, RootModel
from pydantic.fields import FieldInfo

from .utilities import extract_inner_types, get_builtin_types, sanitize_field_name, sanitize_name


class FileManager:
    """Handles all file I/O operations for the build system."""

    def __init__(self) -> None:
        """Initialize the FileManager with empty state."""
        self._generated_files: list[str] = []

    def save_models(
        self,
        models: dict[str, type[BaseModel] | type[list]],
        base_path: str,
        dependency_graph: dict[str, set[str]],
        circular_models: set[str],
        sorted_models: list[str] | None = None,
    ) -> None:
        """
        Save models to individual files and create the __init__.py file.

        Args:
            models: Dictionary of model names to model classes
            base_path: Base directory path where models will be saved
            dependency_graph: Model dependency relationships
            circular_models: Set of models with circular dependencies
            sorted_models: Optional list of models in dependency order
        """
        models_dir = os.path.join(base_path, "models")
        os.makedirs(models_dir, exist_ok=True)

        # Track the models directory creation
        self._generated_files.append(models_dir)

        init_file = os.path.join(models_dir, "__init__.py")
        self._generated_files.append(init_file)

        with open(init_file, "w") as init_f:
            # Write import statements in dependency-aware order to minimize forward references
            self.write_import_statements(init_f, models, models_dir, sorted_models)

            # Import GenericResponseModel from core for backward compatibility
            init_f.write("from ..core.package_models import GenericResponseModel\n")

            for model_name, model in models.items():
                self.save_model_file(
                    model_name,
                    model,
                    models,
                    models_dir,
                    dependency_graph,
                    circular_models,
                    init_f,
                )

            # Add ResponseModelName Literal type
            # Include GenericResponseModel in the Literal since it's a valid response model
            model_names_for_literal = ",\n    ".join(f'"{key}"' for key in sorted(models.keys()))
            init_f.write("from typing import Literal\n\n")
            init_f.write(f"ResponseModelName = Literal[\n    {model_names_for_literal},\n    \"GenericResponseModel\"\n]\n\n")

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
        else:
            model_file.write(f"class {sanitized_model_name}(BaseModel):\n")
            if hasattr(model, "model_fields"):
                self._write_model_fields(model_file, model, models, circular_models)

        # Pydantic model config
        model_file.write(f"\n    {self.get_model_config(sanitized_model_name)}\n")

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
    ) -> None:
        """Write the fields for the model."""
        for field_name, field in model.model_fields.items():
            sanitized_field_name = sanitize_field_name(field_name)

            # Resolve the field's annotation to get the type string, including handling ForwardRefs
            field_type = self._resolve_forward_refs_in_annotation(field.annotation, models, circular_models)

            # Determine field default value based on required status
            field_default = "..." if field.is_required() else "None"

            # For non-required fields, make the type optional (union with None)
            if not field.is_required() and not field_type.endswith(" | None") and field_type != "None":
                field_type = f"{field_type} | None"

            # Only include alias if it differs from the original field name
            if field.alias and field.alias != field_name:
                model_file.write(
                    f"    {sanitized_field_name}: {field_type} = Field({field_default}, alias='{field.alias}')\n"
                )
            else:
                model_file.write(f"    {sanitized_field_name}: {field_type} = Field({field_default})\n")

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
        import re

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
