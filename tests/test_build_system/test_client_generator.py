"""Tests for ClientGenerator class that generates API client classes and configurations."""

import shutil
import tempfile
from pathlib import Path

import pytest

from scripts.build_system.client_generator import ClientGenerator


class TestClientGenerator:
    """Test the ClientGenerator class for API client generation."""

    @pytest.fixture
    def client_generator(self):
        """Create a ClientGenerator instance for testing."""
        return ClientGenerator()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_spec(self):
        """Create a sample OpenAPI specification for testing."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "servers": [
                {"url": "https://api.example.com/v1/test"}
            ],
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "getUsers",
                        "description": "Get all users",
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "integer"},
                                "description": "Maximum number of users to return"
                            }
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/User"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/users/{id}": {
                    "get": {
                        "operationId": "getUserById",
                        "description": "Get user by ID",
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                                "description": "User ID"
                            },
                            {
                                "name": "include_profile",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "boolean"},
                                "description": "Include user profile"
                            }
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"}
                        }
                    }
                }
            }
        }

    @pytest.fixture
    def sample_specs_list(self, sample_spec):
        """Create a list of sample specifications."""
        spec1 = sample_spec.copy()
        spec1["info"]["title"] = "User API"

        spec2 = sample_spec.copy()
        spec2["info"]["title"] = "Order API"
        spec2["servers"] = [{"url": "https://api.example.com/v1/orders"}]

        return [spec1, spec2]

    def test_init_creates_empty_state(self, client_generator):
        """Test that ClientGenerator initializes with empty state."""
        assert hasattr(client_generator, '_generated_clients')
        assert isinstance(client_generator._generated_clients, list)

    def test_extract_api_metadata(self, client_generator, sample_spec):
        """Test extracting API metadata from specification."""
        class_name, api_path, paths = client_generator.extract_api_metadata(sample_spec)

        assert class_name == "TestClient"  # Sanitized from "Test API"
        assert api_path == "/test"  # Extracted from server URL
        assert isinstance(paths, dict)
        assert len(paths) > 0

    def test_classify_parameters(self, client_generator):
        """Test classifying parameters into path and query parameters."""
        parameters = [
            {"name": "id", "in": "path", "required": True},
            {"name": "limit", "in": "query", "required": False},
            {"name": "offset", "in": "query", "required": False},
            {"name": "user_id", "in": "path", "required": True}
        ]

        path_params, query_params = client_generator.classify_parameters(parameters)

        assert "id" in path_params
        assert "user_id" in path_params
        assert "limit" in query_params
        assert "offset" in query_params
        assert len(path_params) == 2
        assert len(query_params) == 2

    def test_method_name_casing_regression(self, client_generator):
        """REGRESSION: Ensure method names are snake_case, not PascalCase."""
        # This prevents the CrowdingClient method name casing bug
        test_cases = [
            ("Naptan", "naptan"),          # Should be lowercase
            ("Live", "live"),              # Should be lowercase
            ("Dayofweek", "dayofweek"),    # Should be lowercase
            ("GetData", "get_data"),       # Should convert to snake_case
            ("getUserById", "get_user_by_id"),  # CamelCase to snake_case
        ]

        for operation_id, expected in test_cases:
            # Test via create_method_signature which calls the method name logic
            parameters = []
            signature = client_generator.create_method_signature(operation_id, parameters, "TestModel")

            # Extract method name from signature
            method_line = signature.split('\n')[0]  # Get first line: "def method_name(self, ...):"
            method_name = method_line.split('(')[0].replace('def ', '').strip()

            assert method_name == expected, f"Expected '{expected}', got '{method_name}' for '{operation_id}'"
            assert method_name.islower() or "_" in method_name, f"Method name '{method_name}' should be lowercase or snake_case"

    def test_method_names_never_pascalcase(self, client_generator):
        """CRITICAL: Method names should never be PascalCase."""
        problematic_inputs = ["Naptan", "Live", "Dayofweek", "GetUsers", "CreateItem"]

        for operation_id in problematic_inputs:
            parameters = []
            signature = client_generator.create_method_signature(operation_id, parameters, "TestModel")

            # Extract method name from signature
            method_line = signature.split('\n')[0]
            method_name = method_line.split('(')[0].replace('def ', '').strip()

            # Check it's not PascalCase (starts with uppercase but contains lowercase)
            if method_name:
                assert not (method_name[0].isupper() and any(c.islower() for c in method_name[1:])), \
                    f"Method name '{method_name}' appears to be PascalCase for input '{operation_id}'"

    def test_create_method_signature(self, client_generator):
        """Test creating method signatures for API operations."""
        operation_id = "getUserById"
        parameters = [
            {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
            {"name": "limit", "in": "query", "required": False, "schema": {"type": "integer"}}
        ]
        model_name = "User"

        signature = client_generator.create_method_signature(operation_id, parameters, model_name)

        assert "def GetUserById(self," in signature
        assert "id: str" in signature
        assert "limit: int | None = None" in signature
        assert "-> ResponseModel[User] | ApiError:" in signature

    def test_create_method_docstring(self, client_generator, sample_spec):
        """Test creating method docstrings."""
        details = sample_spec["paths"]["/users"]["get"]
        full_path = "/test/users"
        model_name = "UserArray"
        parameters = details["parameters"]

        docstring = client_generator.create_method_docstring(details, full_path, model_name, parameters)

        assert "Get all users" in docstring
        assert "Query path: `/test/users`" in docstring
        assert "ResponseModel.content` contains `models.UserArray`" in docstring
        assert "limit`: int" in docstring
        assert "Maximum number of users to return" in docstring

    def test_create_method_implementation_path_params(self, client_generator):
        """Test creating method implementation with path parameters."""
        operation_id = "getUserById"
        parameters = [
            {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
            {"name": "include_profile", "in": "query", "required": False, "schema": {"type": "boolean"}}
        ]

        implementation = client_generator.create_method_implementation(operation_id, parameters)

        assert "params=[id]" in implementation
        assert "'include_profile': include_profile" in implementation
        assert "endpoint_args={" in implementation

    def test_create_method_implementation_query_only(self, client_generator):
        """Test creating method implementation with only query parameters."""
        operation_id = "getUsers"
        parameters = [
            {"name": "limit", "in": "query", "required": False, "schema": {"type": "integer"}}
        ]

        implementation = client_generator.create_method_implementation(operation_id, parameters)

        assert "params=[" not in implementation  # No path params
        assert "'limit': limit" in implementation
        assert "endpoint_args={" in implementation

    def test_create_method_implementation_no_params(self, client_generator):
        """Test creating method implementation with no parameters."""
        operation_id = "getAllUsers"
        parameters = []

        implementation = client_generator.create_method_implementation(operation_id, parameters)

        assert "endpoint_args=None" in implementation
        assert "params=" not in implementation

    def test_process_single_method(self, client_generator, sample_spec):
        """Test processing a single API method."""
        path = "/users/{id}"
        method = "get"
        details = sample_spec["paths"][path][method]
        api_path = "/test"
        all_types = set()
        all_package_models = set()

        method_definition = client_generator.process_single_method(
            path, method, details, api_path, all_types, all_package_models
        )

        assert "def GetUserById(self," in method_definition
        assert "Get user by ID" in method_definition
        assert "_send_request_and_deserialize" in method_definition
        assert len(all_types) > 0  # Should have collected parameter types
        assert len(all_package_models) > 0  # Should have collected model names

    def test_generate_import_lines(self, client_generator):
        """Test generating import statements for client class."""
        class_name = "TestClient"
        all_types = {str, int, bool}
        all_package_models = {"User", "UserArray", "GenericResponseModel"}

        import_lines = client_generator.generate_import_lines(class_name, all_types, all_package_models)

        import_text = "".join(import_lines)

        assert f"from .{class_name}_config import endpoints, base_url" in import_text
        assert "from ..core import ApiError, ResponseModel, Client, GenericResponseModel" in import_text
        assert "from ..models import User, UserArray" in import_text
        assert "GenericResponseModel" not in import_text.split("from ..models import")[1]  # Should be removed from models import

    def test_generate_import_lines_no_generic_response(self, client_generator):
        """Test generating imports when GenericResponseModel is not needed."""
        class_name = "TestClient"
        all_types = {str, int}
        all_package_models = {"User", "UserArray"}

        import_lines = client_generator.generate_import_lines(class_name, all_types, all_package_models)

        import_text = "".join(import_lines)

        assert "from ..core import ApiError, ResponseModel, Client" in import_text
        assert "GenericResponseModel" not in import_text

    def test_create_config(self, client_generator, temp_dir, sample_spec):
        """Test creating configuration file for API client."""
        base_url = "https://api.example.com"

        client_generator.create_config(sample_spec, str(temp_dir), base_url)

        # Check that config file was created
        config_file = temp_dir / "TestClient_config.py"
        assert config_file.exists()

        content = config_file.read_text()

        # Check config content
        assert f'base_url = "{base_url}"' in content
        assert "endpoints = {" in content
        assert "'getUsers':" in content
        assert "'getUserById':" in content
        assert "uri': '/test/users'" in content
        assert "model': 'UserArray'" in content

    def test_create_class(self, client_generator, temp_dir, sample_spec):
        """Test creating API client class file."""
        client_generator.create_class(sample_spec, str(temp_dir))

        # Check that class file was created
        class_file = temp_dir / "TestClient.py"
        assert class_file.exists()

        content = class_file.read_text()

        # Check class content
        assert "class TestClient(Client):" in content
        assert "def GetUsers(self," in content
        assert "def GetUserById(self," in content
        assert "Get all users" in content
        assert "_send_request_and_deserialize" in content

    def test_get_model_name_from_path_object(self, client_generator):
        """Test getting model name from response path for object responses."""
        response_content = {
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/User"}
                }
            }
        }

        model_name = client_generator.get_model_name_from_path(response_content)
        assert model_name == "User"

    def test_get_model_name_from_path_array(self, client_generator):
        """Test getting model name from response path for array responses."""
        response_content = {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/User"}
                    }
                }
            }
        }

        model_name = client_generator.get_model_name_from_path(response_content)
        assert model_name == "UserArray"

    def test_get_model_name_from_path_fallback(self, client_generator):
        """Test getting model name falls back to GenericResponseModel."""
        # Empty response content
        response_content = {}
        model_name = client_generator.get_model_name_from_path(response_content)
        assert model_name == "GenericResponseModel"

        # Missing schema
        response_content = {
            "content": {
                "application/json": {}
            }
        }
        model_name = client_generator.get_model_name_from_path(response_content)
        assert model_name == "GenericResponseModel"

    def test_create_function_parameters(self, client_generator):
        """Test creating function parameter strings."""
        parameters = [
            {
                "name": "id",
                "required": True,
                "schema": {"type": "string"}
            },
            {
                "name": "limit",
                "required": False,
                "schema": {"type": "integer"}
            },
            {
                "name": "optional_param",
                "required": False,
                "schema": {"type": "boolean"}
            }
        ]

        param_str = client_generator.create_function_parameters(parameters)

        # Required parameters should come first without default values
        assert "id: str" in param_str
        # Optional parameters should have default values
        assert "limit: int | None = None" in param_str
        assert "optional_param: bool | None = None" in param_str

    def test_save_classes(self, client_generator, temp_dir, sample_specs_list):
        """Test saving all client classes and configurations."""
        base_url = "https://api.example.com"

        client_generator.save_classes(sample_specs_list, str(temp_dir), base_url)

        # Check main __init__.py
        main_init = temp_dir / "__init__.py"
        assert main_init.exists()

        content = main_init.read_text()
        assert "UserClient" in content
        assert "OrderClient" in content
        assert "from .endpoints import (" in content

        # Check endpoints directory
        endpoints_dir = temp_dir / "endpoints"
        assert endpoints_dir.exists()

        # Check endpoints __init__.py
        endpoints_init = endpoints_dir / "__init__.py"
        assert endpoints_init.exists()

        endpoints_content = endpoints_init.read_text()
        assert "from .UserClient import UserClient" in endpoints_content
        assert "from .OrderClient import OrderClient" in endpoints_content
        assert "TfLEndpoint = Literal[" in endpoints_content

        # Check individual client files
        assert (endpoints_dir / "UserClient.py").exists()
        assert (endpoints_dir / "OrderClient.py").exists()
        assert (endpoints_dir / "UserClient_config.py").exists()
        assert (endpoints_dir / "OrderClient_config.py").exists()

    def test_join_url_paths(self, client_generator):
        """Test URL path joining functionality."""
        # Basic joining
        result = client_generator.join_url_paths("/api/v1", "users")
        assert result == "/api/v1/users"

        # Handle trailing/leading slashes
        result = client_generator.join_url_paths("/api/v1/", "/users")
        assert result == "/api/v1/users"

        # Handle empty base
        result = client_generator.join_url_paths("", "users")
        assert result == "/users"

    def test_get_generated_clients(self, client_generator, temp_dir, sample_specs_list):
        """Test tracking of generated client files."""
        base_url = "https://api.example.com"

        client_generator.save_classes(sample_specs_list, str(temp_dir), base_url)

        generated_clients = client_generator.get_generated_clients()

        # Should track all generated files
        assert len(generated_clients) > 0
        assert any("UserClient.py" in path for path in generated_clients)
        assert any("OrderClient.py" in path for path in generated_clients)
        assert any("UserClient_config.py" in path for path in generated_clients)

    def test_clear_generated_clients(self, client_generator):
        """Test clearing the generated clients list."""
        # Simulate some generated clients
        client_generator._generated_clients = ["client1.py", "client2.py"]

        assert len(client_generator.get_generated_clients()) == 2

        client_generator.clear_generated_clients()

        assert len(client_generator.get_generated_clients()) == 0

    def test_sanitize_operation_id(self, client_generator):
        """Test sanitizing operation IDs for method names."""
        # Should convert to PascalCase
        assert client_generator.sanitize_name("getUserById") == "GetUserById"
        assert client_generator.sanitize_name("get-users") == "Users"
        assert client_generator.sanitize_name("list_all_items") == "Items"

        # Should handle keywords
        assert client_generator.sanitize_name("class") == "Query_Class"

    def test_error_handling_missing_operation_id(self, client_generator):
        """Test handling methods without operation IDs."""
        all_types = set()
        all_package_models = set()

        # Method without operationId should return empty string
        result = client_generator.process_single_method(
            "/test", "get", {}, "/api", all_types, all_package_models
        )

        assert result == ""

    def test_endpoint_path_parameter_replacement(self, client_generator, temp_dir, sample_spec):
        """Test that path parameters are correctly replaced in endpoint URLs."""
        client_generator.create_config(sample_spec, str(temp_dir), "https://api.example.com")

        config_file = temp_dir / "TestClient_config.py"
        content = config_file.read_text()

        # Path parameters should be replaced with format placeholders
        assert "/test/users/{0}" in content  # {id} becomes {0}
