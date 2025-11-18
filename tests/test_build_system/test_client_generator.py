"""Tests for ClientGenerator class that generates API client classes and configurations."""

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from scripts.build_system.client_generator import ClientGenerator


class TestClientGenerator:
    """Test the ClientGenerator class for API client generation."""

    @pytest.fixture
    def client_generator(self) -> ClientGenerator:
        """Create a ClientGenerator instance for testing."""
        return ClientGenerator()

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_spec(self) -> dict[str, Any]:
        """Create a sample OpenAPI specification for testing."""
        return {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "servers": [{"url": "https://api.example.com/v1/test"}],
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
                                "description": "Maximum number of users to return",
                            }
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}
                                    }
                                }
                            }
                        },
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
                                "description": "User ID",
                            },
                            {
                                "name": "include_profile",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "boolean"},
                                "description": "Include user profile",
                            },
                        ],
                        "responses": {
                            "200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}
                        },
                    }
                },
            },
            "components": {
                "schemas": {
                    "User": {"type": "object", "properties": {"id": {"type": "string"}, "name": {"type": "string"}}}
                }
            },
        }

    @pytest.fixture
    def sample_specs_list(self, sample_spec: dict[str, Any]) -> list[dict[str, Any]]:
        """Create a list of sample specifications."""
        spec1 = sample_spec.copy()
        spec1["info"]["title"] = "User API"

        spec2 = sample_spec.copy()
        spec2["info"]["title"] = "Order API"
        spec2["servers"] = [{"url": "https://api.example.com/v1/orders"}]

        return [spec1, spec2]

    def test_init_creates_empty_state(self, client_generator: Any) -> None:
        """Test that ClientGenerator initializes with empty state."""
        assert hasattr(client_generator, "_generated_clients")
        assert isinstance(client_generator._generated_clients, list)

    def test_extract_api_metadata(self, client_generator: Any, sample_spec: Any) -> None:
        """Test extracting API metadata from specification."""
        class_name, api_path, paths = client_generator.extract_api_metadata(sample_spec)

        assert class_name == "TestClient"  # Sanitized from "Test API"
        assert api_path == "/v1/test"  # Full path extracted from server URL
        assert isinstance(paths, dict)
        assert len(paths) > 0

    def test_classify_parameters(self, client_generator: Any) -> None:
        """Test classifying parameters into path and query parameters."""
        parameters = [
            {"name": "id", "in": "path", "required": True},
            {"name": "limit", "in": "query", "required": False},
            {"name": "offset", "in": "query", "required": False},
            {"name": "user_id", "in": "path", "required": True},
        ]

        path_params, query_params = client_generator.classify_parameters(parameters)

        assert "id" in path_params
        assert "user_id" in path_params
        assert "limit" in query_params
        assert "offset" in query_params
        assert len(path_params) == 2
        assert len(query_params) == 2

    def test_method_name_casing_regression(self, client_generator: Any) -> None:
        """REGRESSION: Ensure method names match OpenAPI spec operation IDs (PascalCase)."""
        # This prevents method name inconsistencies with the OpenAPI specification
        test_cases = [
            ("Naptan", "Naptan"),  # Should preserve case from spec
            ("Live", "Live"),  # Should preserve case from spec
            ("Dayofweek", "Dayofweek"),  # Should preserve case from spec
            ("GetData", "GetData"),  # Should preserve PascalCase
            ("getUserById", "GetUserById"),  # Should normalize to PascalCase
        ]

        for operation_id, expected in test_cases:
            # Test via create_method_signature which calls the method name logic
            parameters: list[dict] = []
            signature = client_generator.create_method_signature(operation_id, parameters, "TestModel")

            # Extract method name from signature
            method_line = signature.split("\n")[0]  # Get first line: "def method_name(self, ...):"
            method_name = method_line.split("(")[0].replace("def ", "").strip()

            assert method_name == expected, f"Expected '{expected}', got '{method_name}' for '{operation_id}'"
            assert method_name.isidentifier(), f"Method name '{method_name}' should be a valid Python identifier"

    def test_method_names_follow_openapi_spec(self, client_generator: Any) -> None:
        """CRITICAL: Method names should match OpenAPI specification operation IDs."""
        test_inputs = ["Naptan", "Live", "Dayofweek", "GetUsers", "CreateItem"]

        for operation_id in test_inputs:
            parameters: list[dict] = []
            signature = client_generator.create_method_signature(operation_id, parameters, "TestModel")

            # Extract method name from signature
            method_line = signature.split("\n")[0]
            method_name = method_line.split("(")[0].replace("def ", "").strip()

            # Check method name is a valid Python identifier and matches expected casing
            if method_name:
                assert method_name.isidentifier(), f"Method name '{method_name}' should be valid Python identifier"
                # Method names should preserve the operation ID casing (PascalCase for OpenAPI spec)
                # This ensures consistency with the API specification
                assert method_name == operation_id or method_name.startswith(
                    operation_id[0].upper()
                ), f"Method name '{method_name}' should match OpenAPI operation ID format for '{operation_id}'"

    def test_create_method_signature(self, client_generator: Any) -> None:
        """Test creating method signatures for API operations."""
        operation_id = "getUserById"
        parameters = [
            {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
            {"name": "limit", "in": "query", "required": False, "schema": {"type": "integer"}},
        ]
        model_name = "User"

        signature = client_generator.create_method_signature(operation_id, parameters, model_name)

        assert "def GetUserById(self," in signature
        assert "id: str" in signature
        assert "limit: int | None = None" in signature
        assert "-> ResponseModel[User] | ApiError:" in signature

    def test_create_method_docstring(self, client_generator: Any, sample_spec: Any) -> None:
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

    def test_create_method_implementation_path_params(self, client_generator: Any) -> None:
        """Test creating method implementation with path parameters."""
        operation_id = "getUserById"
        parameters = [
            {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
            {"name": "include_profile", "in": "query", "required": False, "schema": {"type": "boolean"}},
        ]

        implementation = client_generator.create_method_implementation(operation_id, parameters)

        assert "params=[id]" in implementation
        assert "'include_profile': include_profile" in implementation
        assert "endpoint_args={" in implementation

    def test_create_method_implementation_query_only(self, client_generator: Any) -> None:
        """Test creating method implementation with only query parameters."""
        operation_id = "getUsers"
        parameters = [{"name": "limit", "in": "query", "required": False, "schema": {"type": "integer"}}]

        implementation = client_generator.create_method_implementation(operation_id, parameters)

        assert "params=[" not in implementation  # No path params
        assert "'limit': limit" in implementation
        assert "endpoint_args={" in implementation

    def test_create_method_implementation_no_params(self, client_generator: Any) -> None:
        """Test creating method implementation with no parameters."""
        operation_id = "getAllUsers"
        parameters: list[dict] = []

        implementation = client_generator.create_method_implementation(operation_id, parameters)

        assert "endpoint_args=None" in implementation
        assert "params=" not in implementation

    def test_process_single_method(self, client_generator: Any, sample_spec: Any) -> None:
        """Test processing a single API method."""
        path = "/users/{id}"
        method = "get"
        details = sample_spec["paths"][path][method]
        api_path = "/test"
        all_types: set[type] = set()
        all_package_models: set[str] = set()

        method_definition = client_generator.process_single_method(
            path, method, details, api_path, all_types, all_package_models
        )

        assert "def GetUserById(self," in method_definition
        assert "Get user by ID" in method_definition
        assert "_send_request_and_deserialize" in method_definition
        assert len(all_types) > 0  # Should have collected parameter types
        assert len(all_package_models) > 0  # Should have collected model names

    def test_generate_import_lines(self, client_generator: Any) -> None:
        """Test generating import statements for client class."""
        class_name = "TestClient"
        all_types = {str, int, bool}
        all_package_models = {"User", "UserArray", "GenericResponseModel"}

        import_lines = client_generator.generate_import_lines(class_name, all_types, all_package_models)

        import_text = "".join(import_lines)

        assert f"from .{class_name}_config import base_url, endpoints" in import_text
        assert "from ..core import ApiError, Client, GenericResponseModel, ResponseModel" in import_text
        assert "from ..models import User, UserArray" in import_text
        assert (
            "GenericResponseModel" not in import_text.split("from ..models import")[1]
        )  # Should be removed from models import

    def test_generate_import_lines_no_generic_response(self, client_generator: Any) -> None:
        """Test generating imports when GenericResponseModel is not needed."""
        class_name = "TestClient"
        all_types = {str, int}
        all_package_models = {"User", "UserArray"}

        import_lines = client_generator.generate_import_lines(class_name, all_types, all_package_models)

        import_text = "".join(import_lines)

        assert "from ..core import ApiError, Client, ResponseModel" in import_text
        assert "GenericResponseModel" not in import_text

    def test_create_config(self, client_generator: Any, temp_dir: Any, sample_spec: Any) -> None:
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
        assert "uri': '/v1/test/users'" in content  # Full path from server URL
        assert "model': 'UserArray'" in content

    def test_create_class(self, client_generator: Any, temp_dir: Any, sample_spec: Any) -> None:
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

    def test_get_model_name_from_path_object(self, client_generator: Any) -> None:
        """Test getting model name from response path for object responses."""
        response_content = {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}

        model_name = client_generator.get_model_name_from_path(response_content)
        assert model_name == "User"

    def test_get_model_name_from_path_array(self, client_generator: Any) -> None:
        """Test getting model name from response path for array responses."""
        response_content = {
            "content": {
                "application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}}
            }
        }

        model_name = client_generator.get_model_name_from_path(response_content)
        assert model_name == "UserArray"

    def test_get_model_name_from_path_fallback(self, client_generator: Any) -> None:
        """Test getting model name falls back to GenericResponseModel."""
        # Empty response content
        response_content: dict[str, Any] = {}
        model_name = client_generator.get_model_name_from_path(response_content)
        assert model_name == "GenericResponseModel"

        # Missing schema
        response_content = {"content": {"application/json": {}}}
        model_name = client_generator.get_model_name_from_path(response_content)
        assert model_name == "GenericResponseModel"

    def test_create_function_parameters(self, client_generator: Any) -> None:
        """Test creating function parameter strings."""
        parameters = [
            {"name": "id", "required": True, "schema": {"type": "string"}},
            {"name": "limit", "required": False, "schema": {"type": "integer"}},
            {"name": "optional_param", "required": False, "schema": {"type": "boolean"}},
        ]

        param_str = client_generator.create_function_parameters(parameters)

        # Required parameters should come first without default values
        assert "id: str" in param_str
        # Optional parameters should have default values
        assert "limit: int | None = None" in param_str
        assert "optional_param: bool | None = None" in param_str

    def test_save_classes(self, client_generator: Any, temp_dir: Any, sample_specs_list: Any) -> None:
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
        # New format exports both sync and async clients
        assert "from .UserClient import AsyncUserClient, UserClient" in endpoints_content
        assert "from .OrderClient import AsyncOrderClient, OrderClient" in endpoints_content
        assert "TfLEndpoint = Literal[" in endpoints_content
        assert "AsyncTfLEndpoint = Literal[" in endpoints_content

        # Check individual client files
        assert (endpoints_dir / "UserClient.py").exists()
        assert (endpoints_dir / "OrderClient.py").exists()
        assert (endpoints_dir / "UserClient_config.py").exists()
        assert (endpoints_dir / "OrderClient_config.py").exists()

    def test_join_url_paths(self, client_generator: Any) -> None:
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

    def test_get_generated_clients(self, client_generator: Any, temp_dir: Any, sample_specs_list: Any) -> None:
        """Test tracking of generated client files."""
        base_url = "https://api.example.com"

        client_generator.save_classes(sample_specs_list, str(temp_dir), base_url)

        generated_clients = client_generator.get_generated_clients()

        # Should track all generated files
        assert len(generated_clients) > 0
        assert any("UserClient.py" in path for path in generated_clients)
        assert any("OrderClient.py" in path for path in generated_clients)
        assert any("UserClient_config.py" in path for path in generated_clients)

    def test_clear_generated_clients(self, client_generator: Any) -> None:
        """Test clearing the generated clients list."""
        # Simulate some generated clients
        client_generator._generated_clients = ["client1.py", "client2.py"]

        assert len(client_generator.get_generated_clients()) == 2

        client_generator.clear_generated_clients()

        assert len(client_generator.get_generated_clients()) == 0

    def test_sanitize_operation_id(self, client_generator: Any) -> None:
        """Test sanitizing operation IDs for method names."""
        # Should convert to PascalCase
        assert client_generator.sanitize_name("getUserById") == "GetUserById"
        assert client_generator.sanitize_name("get-users") == "Users"
        assert client_generator.sanitize_name("list_all_items") == "Items"

        # Should handle keywords
        assert client_generator.sanitize_name("class") == "Query_Class"

    def test_error_handling_missing_operation_id(self, client_generator: Any) -> None:
        """Test handling methods without operation IDs."""
        all_types: set[type] = set()
        all_package_models: set[str] = set()

        # Method without operationId should return empty string
        result = client_generator.process_single_method("/test", "get", {}, "/api", all_types, all_package_models)

        assert result == ""

    def test_endpoint_path_parameter_replacement(self, client_generator: Any, temp_dir: Any, sample_spec: Any) -> None:
        """Test that path parameters are correctly replaced in endpoint URLs."""
        client_generator.create_config(sample_spec, str(temp_dir), "https://api.example.com")

        config_file = temp_dir / "TestClient_config.py"
        content = config_file.read_text()

        # Path parameters should be replaced with format placeholders
        assert "/test/users/{0}" in content  # {id} becomes {0}

    def test_extract_full_path_from_server_url(self, client_generator: Any) -> None:
        """REGRESSION: Test that full path is extracted from server URL, not just last segment."""
        # This prevents the "/v2/" bug where only the last segment was extracted

        # Test nested path like TfL's Lift Disruptions API
        spec_nested = {
            "info": {"title": "Lift Disruptions"},
            "servers": [{"url": "https://api.tfl.gov.uk/Disruptions/Lifts/v2"}],
            "paths": {"/": {}},
        }
        _, api_path, _ = client_generator.extract_api_metadata(spec_nested)
        assert api_path == "/Disruptions/Lifts/v2", f"Expected '/Disruptions/Lifts/v2', got '{api_path}'"

        # Test simple path
        spec_simple = {
            "info": {"title": "Bike Point"},
            "servers": [{"url": "https://api.tfl.gov.uk/BikePoint"}],
            "paths": {"/": {}},
        }
        _, api_path, _ = client_generator.extract_api_metadata(spec_simple)
        assert api_path == "/BikePoint", f"Expected '/BikePoint', got '{api_path}'"

        # Test root path
        spec_root = {"info": {"title": "Root API"}, "servers": [{"url": "https://api.example.com"}], "paths": {"/": {}}}
        _, api_path, _ = client_generator.extract_api_metadata(spec_root)
        assert api_path == "", f"Expected '', got '{api_path}'"

    def test_config_uses_full_server_path(self, client_generator: Any, temp_dir: Any) -> None:
        """REGRESSION: Test that config files use the full server path in endpoint URIs."""
        spec = {
            "info": {"title": "Lift Disruptions"},
            "servers": [{"url": "https://api.tfl.gov.uk/Disruptions/Lifts/v2"}],
            "paths": {
                "/": {
                    "get": {
                        "operationId": "get",
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/LiftDisruption"},
                                        }
                                    }
                                }
                            }
                        },
                    }
                }
            },
        }

        client_generator.create_config(spec, str(temp_dir), "https://api.tfl.gov.uk")

        config_file = temp_dir / "LiftDisruptionsClient_config.py"
        content = config_file.read_text()

        # Should contain full path, not just "/v2/"
        assert "'/Disruptions/Lifts/v2/'" in content, f"Expected full path in config, got: {content}"
        assert "'uri': '/v2/'" not in content, "Should not have partial path /v2/"


class TestAsyncClientGeneration:
    """Test async client generation features."""

    @pytest.fixture
    def client_generator(self) -> ClientGenerator:
        """Create a ClientGenerator instance for testing."""
        return ClientGenerator()

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_spec(self) -> dict[str, Any]:
        """Create a sample OpenAPI specification for testing."""
        return {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "servers": [{"url": "https://api.example.com/v1/test"}],
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
                            }
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}
                                    }
                                }
                            }
                        },
                    }
                },
            },
        }

    def test_create_async_method_signature(self, client_generator: Any) -> None:
        """Test creating async method signatures."""
        operation_id = "getUserById"
        parameters = [
            {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
        ]
        model_name = "User"

        signature = client_generator.create_method_signature(operation_id, parameters, model_name, is_async=True)

        assert "async def GetUserById(self," in signature
        assert "-> ResponseModel[User] | ApiError:" in signature

    def test_create_async_method_implementation(self, client_generator: Any) -> None:
        """Test creating async method implementations with await."""
        operation_id = "getUsers"
        parameters: list[dict[str, Any]] = []

        implementation = client_generator.create_method_implementation(operation_id, parameters, is_async=True)

        assert "return await self._send_request_and_deserialize" in implementation

    def test_create_sync_method_implementation(self, client_generator: Any) -> None:
        """Test that sync methods don't have await."""
        operation_id = "getUsers"
        parameters: list[dict[str, Any]] = []

        implementation = client_generator.create_method_implementation(operation_id, parameters, is_async=False)

        assert "return self._send_request_and_deserialize" in implementation
        assert "await" not in implementation

    def test_generate_import_lines_with_async(self, client_generator: Any) -> None:
        """Test that import lines include AsyncClient when include_async=True."""
        all_types: set[type] = set()
        all_package_models: set[str] = {"User"}

        import_lines = client_generator.generate_import_lines("TestClient", all_types, all_package_models, include_async=True)
        import_content = "".join(import_lines)

        assert "AsyncClient" in import_content
        assert "Client" in import_content

    def test_generate_import_lines_without_async(self, client_generator: Any) -> None:
        """Test that import lines don't include AsyncClient when include_async=False."""
        all_types: set[type] = set()
        all_package_models: set[str] = {"User"}

        import_lines = client_generator.generate_import_lines("TestClient", all_types, all_package_models, include_async=False)
        import_content = "".join(import_lines)

        assert "AsyncClient" not in import_content
        assert "Client" in import_content

    def test_create_class_generates_both_sync_and_async(self, client_generator: Any, temp_dir: Any, sample_spec: Any) -> None:
        """Test that create_class generates both sync and async client classes."""
        client_generator.create_class(sample_spec, str(temp_dir))

        class_file = temp_dir / "TestClient.py"
        assert class_file.exists()

        content = class_file.read_text()

        # Check sync class
        assert "class TestClient(Client):" in content

        # Check async class
        assert "class AsyncTestClient(AsyncClient):" in content

        # Check async method
        assert "async def GetUsers" in content
        assert "await self._send_request_and_deserialize" in content

    def test_save_classes_exports_async_clients(self, client_generator: Any, temp_dir: Any) -> None:
        """Test that save_classes exports both sync and async clients."""
        # Create a simple spec with a known name (avoid "Test" which gets normalized to "User")
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Sample API", "version": "1.0.0"},
            "servers": [{"url": "https://api.example.com/v1/test"}],
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "getUsers",
                        "parameters": [],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}
                                    }
                                }
                            }
                        },
                    }
                },
            },
        }
        specs = [spec]

        client_generator.save_classes(specs, str(temp_dir), "https://api.example.com")

        # Check main __init__.py
        init_file = temp_dir / "__init__.py"
        init_content = init_file.read_text()

        assert "SampleClient" in init_content
        assert "AsyncSampleClient" in init_content

        # Check endpoints __init__.py
        endpoints_init = temp_dir / "endpoints" / "__init__.py"
        endpoints_content = endpoints_init.read_text()

        assert "from .SampleClient import AsyncSampleClient, SampleClient" in endpoints_content
        assert "TfLEndpoint" in endpoints_content
        assert "AsyncTfLEndpoint" in endpoints_content

    def test_process_single_method_async(self, client_generator: Any) -> None:
        """Test processing a single method with is_async=True."""
        all_types: set[type] = set()
        all_package_models: set[str] = set()

        details = {
            "operationId": "getUsers",
            "parameters": [],
            "responses": {
                "200": {
                    "content": {
                        "application/json": {
                            "schema": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}
                        }
                    }
                }
            },
        }

        result = client_generator.process_single_method(
            "/users", "get", details, "/api", all_types, all_package_models, is_async=True
        )

        assert "async def GetUsers" in result
        assert "await self._send_request_and_deserialize" in result

    def test_async_method_with_path_params(self, client_generator: Any) -> None:
        """Test async method generation with path parameters."""
        operation_id = "getUserById"
        parameters = [
            {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
        ]

        implementation = client_generator.create_method_implementation(operation_id, parameters, is_async=True)

        assert "await" in implementation
        assert "params=[id]" in implementation

    def test_async_method_with_query_params(self, client_generator: Any) -> None:
        """Test async method generation with query parameters."""
        operation_id = "getUsers"
        parameters = [
            {"name": "limit", "in": "query", "required": False, "schema": {"type": "integer"}},
        ]

        implementation = client_generator.create_method_implementation(operation_id, parameters, is_async=True)

        assert "await" in implementation
        assert "'limit': limit" in implementation
