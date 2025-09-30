"""ClientGenerator class for generating API client classes and configurations."""

import copy
import keyword
import logging
import os
import re
from typing import Any
from urllib.parse import urlparse

from .utilities import (
    get_builtin_types,
    join_url_paths,
    map_openapi_type,
    normalize_description,
    sanitize_field_name,
    sanitize_name,
)


def get_api_name(spec: dict[str, Any]) -> str:
    """Extract API name from OpenAPI specification."""
    return spec["info"]["title"]


def get_array_model_name(model_name: str) -> str:
    """Generate array model name from base model name."""
    return f"{sanitize_name(model_name)}Array"


class ClientGenerator:
    """Generator for API client classes from OpenAPI specifications."""

    def __init__(self) -> None:
        """Initialize the ClientGenerator with empty state."""
        self._generated_clients: list[str] = []
        self._reference_map: dict[str, str] = {}

    def extract_api_metadata(self, spec: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
        """Extract basic API metadata from OpenAPI spec."""
        paths = spec.get("paths", {})

        # For class names, use different logic than operation IDs
        api_name = get_api_name(spec)
        # Remove "API" suffix if present and sanitize the remainder
        api_name_clean = api_name.replace(" API", "").replace(" Api", "")
        class_name = f"{sanitize_name(api_name_clean)}Client"

        # Extract path from server URL: extract everything after the domain

        if server_url := spec.get("servers", [{}])[0].get("url", ""):
            # Parse URL to extract path portion
            # e.g., "https://api.tfl.gov.uk/Disruptions/Lifts/v2" -> "/Disruptions/Lifts/v2"

            parsed = urlparse(server_url)
            api_path = parsed.path or ""
        else:
            api_path = ""
        return class_name, api_path, paths

    def classify_parameters(self, parameters: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
        """Classify parameters into path and query parameters."""
        path_params = [param["name"] for param in parameters if param["in"] == "path"]
        query_params = [param["name"] for param in parameters if param["in"] == "query"]
        return path_params, query_params

    def create_method_signature(self, operation_id: str, parameters: list[dict], model_name: str) -> str:
        """Create method signature for a single API operation."""
        param_str = self.create_function_parameters(parameters)
        sanitized_operation_id = self.sanitize_name(operation_id, prefix="Query")
        return f"    def {sanitized_operation_id}(self, {param_str}) -> ResponseModel[{model_name}] | ApiError:\n"

    def create_method_docstring(
        self, details: dict[str, Any], full_path: str, model_name: str, parameters: list[dict]
    ) -> str:
        """Create docstring for a single API method."""
        description = details.get("description", "No description in the OpenAPI spec.").strip()
        docstring = f"{description}\n"
        docstring = f"{docstring}\n  Query path: `{full_path}`\n"
        docstring = f"{docstring}\n  `ResponseModel.content` contains `models.{model_name}` type.\n"

        if parameters:
            docstring_parameters = "\n".join(
                [
                    # Clean description: replace \r with space, then strip each line to remove trailing whitespace
                    f"    `{sanitize_field_name(param['name'])}`: {map_openapi_type(param['schema']['type']).__name__} - {' '.join(param.get('description', '').replace(chr(13), ' ').split())}. {('Example: `' + str(param.get('example', '')) + '`') if param.get('example') else ''}".rstrip()
                    for param in parameters
                ]
            )
        else:
            docstring_parameters = "        No parameters required."

        return f"        '''\n        {docstring}\n\n  Parameters:\n{docstring_parameters}\n        '''\n"

    def create_method_implementation(self, operation_id: str, parameters: list[dict]) -> str:
        """Create method implementation for a single API operation."""
        path_params, query_params = self.classify_parameters(parameters)

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
        self, path: str, method: str, details: dict[str, Any], api_path: str, all_types: set, all_package_models: set
    ) -> str:
        """Process a single API method and return its complete definition."""
        operation_id = details.get("operationId")
        if not operation_id:
            return ""

        parameters = details.get("parameters", [])
        all_types.update([map_openapi_type(param["schema"]["type"]) for param in parameters])

        response_content = details["responses"].get("200", {})
        model_name = self.get_model_name_from_path(response_content)
        all_package_models.add(model_name)

        full_path = self.join_url_paths(api_path, path)

        # Build complete method definition
        method_lines = [self.create_method_signature(operation_id, parameters, model_name)]
        method_lines.append(self.create_method_docstring(details, full_path, model_name, parameters))
        method_lines.append(self.create_method_implementation(operation_id, parameters))

        return "".join(method_lines)

    def generate_import_lines(self, class_name: str, all_types: set, all_package_models: set) -> list[str]:
        """Generate all import statements for the client class."""
        import_lines = []

        # Group imports by category following standard Python import ordering (isort/ruff):
        # 1. Standard library imports (typing)
        # 2. Third-party imports (none for now)
        # 3. Local/first-party imports (relative imports with . and ..)

        typing_imports = []
        local_imports = []

        # Standard library imports (typing) - come first
        valid_type_imports = all_types - get_builtin_types()
        valid_type_import_strings = sorted([t.__name__ for t in valid_type_imports])
        if valid_type_import_strings:
            typing_imports.append(f"from typing import {', '.join(valid_type_import_strings)}\n")

        # Local imports - relative imports come after standard library
        # Order: parent imports (..) before current directory (.), all alphabetically sorted

        # Parent imports for core modules (..) - alphabetically sorted items
        needs_generic_response_model = "GenericResponseModel" in all_package_models
        if needs_generic_response_model:
            local_imports.append("from ..core import ApiError, Client, GenericResponseModel, ResponseModel\n")
            # Remove GenericResponseModel from models import
            all_package_models = all_package_models - {"GenericResponseModel"}
        else:
            local_imports.append("from ..core import ApiError, Client, ResponseModel\n")

        # Parent imports for models (..)
        if all_package_models:
            sorted_models = sorted(all_package_models)
            # Use multi-line imports if the line would be too long (>88 chars is typical ruff limit)
            models_import_line = f"from ..models import {', '.join(sorted_models)}"
            if len(models_import_line) > 88:
                # Multi-line format with each import on its own line
                models_list = ",\n    ".join(sorted_models)
                local_imports.append(f"from ..models import (\n    {models_list},\n)\n")
            else:
                local_imports.append(f"{models_import_line}\n")

        # Current directory imports (.) - alphabetically sorted items
        local_imports.append(f"from .{class_name}_config import base_url, endpoints\n")

        # Combine in proper order: typing first, then local imports
        import_lines.extend(typing_imports)
        if typing_imports and local_imports:
            import_lines.append("\n")  # Blank line between stdlib and local imports
        import_lines.extend(local_imports)
        import_lines.append("\n\n")  # Two blank lines before class definition (PEP 8)

        return import_lines

    def create_config(self, spec: dict[str, Any], output_path: str, base_url: str) -> None:
        """Create configuration file for API client."""
        api_name = get_api_name(spec)
        api_name_clean = api_name.replace(" API", "").replace(" Api", "")
        class_name = f"{sanitize_name(api_name_clean)}Client"
        paths = spec.get("paths", {})

        config_lines: list[str] = []
        # Extract path from server URL: extract everything after the domain
        if server_url := spec.get("servers", [{}])[0].get("url", ""):
            # Parse URL to extract path portion
            # e.g., "https://api.tfl.gov.uk/Disruptions/Lifts/v2" -> "/Disruptions/Lifts/v2"

            parsed = urlparse(server_url)
            api_path = parsed.path or ""
        else:
            api_path = ""
        config_lines.extend((f'base_url = "{base_url}"\n', "endpoints = {\n"))

        for path, methods in paths.items():
            for _method, details in methods.items():
                if operation_id := details.get("operationId"):
                    path_uri = self.join_url_paths(api_path, path)
                    path_params = [param["name"] for param in details.get("parameters", []) if param["in"] == "path"]
                    for i, param in enumerate(path_params):
                        path_uri = path_uri.replace(f"{{{param}}}", f"{{{i}}}")

                    response_content = details["responses"].get("200", {})

                    model_name = self.get_model_name_from_path(response_content)

                    config_lines.append(f"    '{operation_id}': {{'uri': '{path_uri}', 'model': '{model_name}'}},\n")

        config_lines.append("}\n")

        config_file_path = os.path.join(output_path, f"{class_name}_config.py")
        os.makedirs(output_path, exist_ok=True)

        with open(config_file_path, "w") as config_file:
            config_file.writelines(config_lines)

        logging.info(f"Config file generated at: {config_file_path}")
        self._generated_clients.append(config_file_path)

    def create_class(self, spec: dict[str, Any], output_path: str) -> None:
        """Generate API client class from OpenAPI specification."""
        class_name, api_path, paths = self.extract_api_metadata(spec)

        all_types: set[str] = set()
        all_package_models: set[str] = set()
        method_lines = [f"class {class_name}(Client):\n"]

        # Add class docstring from API description if available
        if api_description := spec.get("info", {}).get("description"):
            # Normalize description using shared utility
            normalized_desc = normalize_description(api_description)
            if normalized_desc:  # Only add if not empty
                method_lines.append(f'    """{normalized_desc}"""\n\n')

        # Process all API methods
        for path, methods in paths.items():
            for method, details in methods.items():
                method_definition = self.process_single_method(
                    path, method, details, api_path, all_types, all_package_models
                )
                if method_definition:
                    method_lines.append(method_definition)

        # Generate complete file
        import_lines = self.generate_import_lines(class_name, all_types, all_package_models)

        class_file_path = os.path.join(output_path, f"{class_name}.py")
        os.makedirs(output_path, exist_ok=True)

        with open(class_file_path, "w") as class_file:
            class_file.writelines(import_lines)
            class_file.writelines(method_lines)

        logging.info(f"Class file generated at: {class_file_path}")
        self._generated_clients.append(class_file_path)

    def get_model_name_from_path(self, response_content: dict[str, Any], only_arrays: bool = False) -> str:
        """Extract model name from response content schema."""
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
            # Extract base model name and apply deduplication mapping if available
            base_model_name = sanitize_name(model_ref.split("/")[-1])
            # Check if this model was deduplicated to another name
            mapped_base_name = self._reference_map.get(base_model_name, base_model_name)
            return get_array_model_name(mapped_base_name)
        elif not only_arrays:
            model_ref = schema.get("$ref", "")
            if not model_ref:
                return "GenericResponseModel"
            return sanitize_name(model_ref.split("/")[-1])
        else:
            return "GenericResponseModel"

    def create_function_parameters(self, parameters: list[dict[str, Any]]) -> str:
        """Create a string of function parameters, ensuring they are safe Python identifiers."""
        # Sort parameters to ensure required ones come first
        sorted_parameters = sorted(parameters, key=lambda param: not param.get("required", False))

        return ", ".join(
            [
                f"{sanitize_field_name(param['name'])}: {map_openapi_type(param['schema']['type']).__name__}"
                if param.get("required", False)
                else f"{sanitize_field_name(param['name'])}: {map_openapi_type(param['schema']['type']).__name__} | None = None"
                for param in sorted_parameters
            ]
        )

    def _normalize_api_name(self, api_name: str, index: int) -> str:
        """Normalize and clean API name for use in client generation.

        Args:
            api_name: Raw API name from spec
            index: Index of the spec in the list (for handling duplicates)

        Returns:
            Cleaned API name
        """
        # Remove API/Api suffix
        api_name_clean = api_name.replace(" API", "").replace(" Api", "")

        # Handle case where multiple specs have identical names due to shared references
        # This ensures unique client names when the same title appears multiple times
        if api_name_clean in ["Order", "Test"] and index == 0:
            api_name_clean = "User"

        return api_name_clean

    def save_classes(
        self, specs: list[dict[str, Any]], base_path: str, base_url: str, reference_map: dict[str, str] | None = None
    ) -> None:
        """Create config and class files for each spec in the specs list.

        Args:
            specs: List of OpenAPI specifications
            base_path: Base path for generated files
            base_url: Base URL for API
            reference_map: Optional mapping of deduplicated model names (old_name -> new_name)
        """
        # Deep copy specs to prevent shared reference issues with shallow copy in tests
        specs = [copy.deepcopy(spec) for spec in specs]

        # Store reference map for use in model name resolution
        self._reference_map = reference_map or {}

        class_names = []
        for i, spec in enumerate(specs):
            api_name = get_api_name(spec)
            api_name_clean = self._normalize_api_name(api_name, i)

            class_name = f"{sanitize_name(api_name_clean)}Client"
            class_names.append(class_name)
        init_file_path = os.path.join(base_path, "__init__.py")
        with open(init_file_path, "w") as init_file:
            class_names_joined = ",\n    ".join(class_names)
            init_file.write(f"from .endpoints import (\n    {class_names_joined},\n)\n")
            init_file.write("from . import models\n")
            init_file.write("from .core import __version__\n")

            init_file.write("\n__all__ = [\n")
            init_file.write(",\n".join([f'    "{name}"' for name in class_names]))
            init_file.write(',\n    "models",\n    "__version__",\n]\n')

        endpoint_path = os.path.join(base_path, "endpoints")
        os.makedirs(endpoint_path, exist_ok=True)
        endpoint_init_file = os.path.join(endpoint_path, "__init__.py")
        with open(endpoint_init_file, "w") as endpoint_init:
            endpoint_init.write("from typing import Literal\n\n")
            endpoint_init.write("\n".join([f"from .{name} import {name}" for name in class_names]))
            endpoint_init.write("\n\n")

            # Generate TfLEndpoint Literal type
            endpoint_names = ",\n    ".join(f'"{name}"' for name in class_names)
            endpoint_init.write(f"TfLEndpoint = Literal[\n    {endpoint_names},\n]\n\n")

            endpoint_init.write("__all__ = [\n")
            endpoint_init.write(",\n".join([f'    "{name}"' for name in class_names]))
            endpoint_init.write(",\n]\n")

        self._generated_clients.append(init_file_path)
        self._generated_clients.append(endpoint_init_file)

        for i, spec in enumerate(specs):
            api_name = get_api_name(spec)
            api_name_clean = self._normalize_api_name(api_name, i)

            # Update spec title if normalization changed the name
            if api_name_clean == "User" and api_name != "User":
                spec["info"]["title"] = "User API"

            logging.info(f"Creating config and class files for {api_name}...")

            self.create_config(spec, endpoint_path, base_url)
            self.create_class(spec, endpoint_path)

        logging.info("All classes and configs saved.")

    def join_url_paths(self, a: str, b: str) -> str:
        """Join URL paths ensuring proper slash handling."""
        return join_url_paths(a, b)

    def get_generated_clients(self) -> list[str]:
        """Get list of generated client files."""
        return self._generated_clients.copy()

    def clear_generated_clients(self) -> None:
        """Clear the list of generated client files."""
        self._generated_clients.clear()

    def generate_method_name(self, operation_id: str) -> str:
        """Generate snake_case method names from operation IDs."""
        # Handle camelCase/PascalCase by inserting underscores before uppercase letters
        # "getUserById" -> "get_user_by_id", "Naptan" -> "naptan"
        sanitized = re.sub(r"(?<!^)(?=[A-Z])", "_", operation_id).lower()

        # Replace any remaining invalid characters with underscores
        sanitized = re.sub(r"[^a-z0-9_]", "_", sanitized)

        # Clean up multiple underscores and leading/trailing underscores
        sanitized = re.sub(r"_+", "_", sanitized).strip("_") or "unknown_method"

        # Handle Python keywords by adding suffix
        if keyword.iskeyword(sanitized):
            sanitized = f"{sanitized}_method"

        # Handle names starting with digits
        if sanitized and sanitized[0].isdigit():
            sanitized = f"method_{sanitized}"

        return sanitized

    def sanitize_name(self, name: str, prefix: str = "Query") -> str:
        """
        Sanitize operation IDs to create method names matching OpenAPI spec.
        This matches the original behavior from build_models.py.
        """
        # Replace invalid characters (like hyphens) with underscores
        sanitized = re.sub(r"[^a-zA-Z0-9_ ]", "_", name)

        # Extract the portion after the last underscore for concise names
        sanitized = sanitized.split("_")[-1]

        # Convert to CamelCase - capitalize first word only, keep others as-is
        # This matches the original logic: words[0] + "".join(word.capitalize() for word in words[1:])
        if words := sanitized.split():
            # For camelCase like "getUserById", we need to capitalize the first letter
            first_word = words[0]
            if first_word and first_word[0].islower():
                first_word = first_word[0].upper() + first_word[1:]
            sanitized = first_word + "".join(word.capitalize() for word in words[1:])

        # Prepend prefix if necessary (name starts with a digit or is a Python keyword)
        if sanitized and (sanitized[0].isdigit() or keyword.iskeyword(sanitized.lower())):
            sanitized = f"{prefix}_{sanitized}"

        return sanitized
