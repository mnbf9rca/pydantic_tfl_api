"""Tests for the HTTP client abstraction layer.

These tests verify the generic abstraction layer that works with any HTTP backend.
Backend-specific tests are in test_httpx_support.py and test_requests_support.py.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from pydantic_tfl_api.core import Client, HTTPClientBase, HTTPResponse, RestClient, UnifiedResponse
from pydantic_tfl_api.core.http_backends.httpx_client import HttpxClient


class TestHTTPClientBase:
    """Tests for the HTTPClientBase abstract class."""

    def test_cannot_instantiate_directly(self) -> None:
        """Test that HTTPClientBase cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            HTTPClientBase()  # type: ignore[abstract]

    def test_subclass_must_implement_get(self) -> None:
        """Test that subclasses must implement the get method."""

        class IncompleteClient(HTTPClientBase):
            pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteClient()  # type: ignore[abstract]


class TestUnifiedResponse:
    """Tests for the UnifiedResponse wrapper class."""

    @pytest.fixture
    def mock_http_response(self) -> Mock:
        """Create a mock HTTPResponse for testing."""
        mock = Mock()
        mock.status_code = 200
        mock.headers = {"Content-Type": "application/json"}
        mock.text = '{"data": "test"}'
        mock.url = "http://test.com/api"
        mock.reason = "OK"
        mock.json.return_value = {"data": "test"}
        return mock

    def test_status_code(self, mock_http_response: Mock) -> None:
        """Test status_code property."""
        response = UnifiedResponse(mock_http_response)
        assert response.status_code == 200

    def test_headers(self, mock_http_response: Mock) -> None:
        """Test headers property."""
        response = UnifiedResponse(mock_http_response)
        assert response.headers == {"Content-Type": "application/json"}

    def test_text(self, mock_http_response: Mock) -> None:
        """Test text property."""
        response = UnifiedResponse(mock_http_response)
        assert response.text == '{"data": "test"}'

    def test_url(self, mock_http_response: Mock) -> None:
        """Test url property."""
        response = UnifiedResponse(mock_http_response)
        assert response.url == "http://test.com/api"

    def test_reason(self, mock_http_response: Mock) -> None:
        """Test reason property."""
        response = UnifiedResponse(mock_http_response)
        assert response.reason == "OK"

    def test_json(self, mock_http_response: Mock) -> None:
        """Test json method."""
        response = UnifiedResponse(mock_http_response)
        assert response.json() == {"data": "test"}

    def test_raise_for_status(self, mock_http_response: Mock) -> None:
        """Test raise_for_status method."""
        response = UnifiedResponse(mock_http_response)
        response.raise_for_status()
        mock_http_response.raise_for_status.assert_called_once()

    def test_ok_for_success(self, mock_http_response: Mock) -> None:
        """Test ok property returns True for successful responses."""
        response = UnifiedResponse(mock_http_response)
        assert response.ok is True

    def test_ok_for_error(self) -> None:
        """Test ok property returns False for error responses."""
        mock = Mock()
        mock.status_code = 400
        response = UnifiedResponse(mock)
        assert response.ok is False

    def test_is_error_for_success(self, mock_http_response: Mock) -> None:
        """Test is_error property returns False for successful responses."""
        response = UnifiedResponse(mock_http_response)
        assert response.is_error is False

    def test_is_error_for_error(self) -> None:
        """Test is_error property returns True for error responses."""
        mock = Mock()
        mock.status_code = 500
        response = UnifiedResponse(mock)
        assert response.is_error is True

    def test_is_client_error(self) -> None:
        """Test is_client_error property."""
        mock = Mock()

        # Test 4xx status codes
        for status in [400, 401, 403, 404, 422, 499]:
            mock.status_code = status
            response = UnifiedResponse(mock)
            assert response.is_client_error is True, f"Expected True for status {status}"

        # Test non-4xx status codes
        for status in [200, 300, 500]:
            mock.status_code = status
            response = UnifiedResponse(mock)
            assert response.is_client_error is False, f"Expected False for status {status}"

    def test_is_server_error(self) -> None:
        """Test is_server_error property."""
        mock = Mock()

        # Test 5xx status codes
        for status in [500, 501, 502, 503, 504]:
            mock.status_code = status
            response = UnifiedResponse(mock)
            assert response.is_server_error is True, f"Expected True for status {status}"

        # Test non-5xx status codes
        for status in [200, 400, 404]:
            mock.status_code = status
            response = UnifiedResponse(mock)
            assert response.is_server_error is False, f"Expected False for status {status}"


class TestRestClientWithHTTPClientAbstraction:
    """Tests for RestClient with the new HTTP client abstraction."""

    def test_default_http_client_is_httpx_client(self) -> None:
        """Test that RestClient uses HttpxClient by default."""
        client = RestClient()
        assert isinstance(client.http_client, HttpxClient)

    def test_custom_http_client_injection(self) -> None:
        """Test that a custom HTTP client can be injected."""

        class CustomClient(HTTPClientBase):
            def get(
                self,
                url: str,
                headers: dict[str, str] | None = None,
                timeout: int | None = None,
            ) -> HTTPResponse:
                mock = Mock()
                mock.status_code = 200
                mock.headers = {}
                mock.text = ""
                mock.url = url
                mock.reason = "OK"
                mock.json.return_value = {}
                return mock

        custom_client = CustomClient()
        rest_client = RestClient(http_client=custom_client)
        assert rest_client.http_client is custom_client

    def test_send_request_returns_unified_response(self) -> None:
        """Test that send_request returns a UnifiedResponse."""
        # Create mock HTTP client
        mock_http_client = Mock(spec=HTTPClientBase)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "{}"
        mock_response.url = "http://test.com"
        mock_response.reason = "OK"
        mock_http_client.get.return_value = mock_response

        client = RestClient(http_client=mock_http_client)
        result = client.send_request("http://api.tfl.gov.uk/", "Line/victoria")

        assert isinstance(result, UnifiedResponse)

    def test_app_key_included_in_headers(self) -> None:
        """Test that app_key is included in request headers."""
        # Create mock HTTP client that captures the call
        mock_http_client = Mock(spec=HTTPClientBase)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = mock_response

        client = RestClient(app_key="test_key", http_client=mock_http_client)
        client.send_request("http://api.tfl.gov.uk/", "Line/victoria")

        # Verify the headers passed to the HTTP client
        call_args = mock_http_client.get.call_args
        headers = call_args.kwargs.get("headers") or call_args[1].get("headers")
        assert headers["app_key"] == "test_key"


class TestClientWithHTTPClientAbstraction:
    """Tests for Client with the new HTTP client abstraction."""

    def test_default_client_works(self) -> None:
        """Test that Client works with default HTTP client."""
        client = Client()
        assert isinstance(client.client.http_client, HttpxClient)

    def test_custom_http_client_passed_through(self) -> None:
        """Test that custom HTTP client is passed to RestClient."""

        class MockHTTPClient(HTTPClientBase):
            def get(
                self,
                url: str,
                headers: dict[str, str] | None = None,
                timeout: int | None = None,
            ) -> HTTPResponse:
                mock = Mock()
                mock.status_code = 200
                return mock

        mock_client = MockHTTPClient()
        client = Client(http_client=mock_client)
        assert client.client.http_client is mock_client

    def test_backward_compatibility_with_api_token(self) -> None:
        """Test backward compatibility - Client can still be created with just api_token."""
        client = Client("test_token")
        assert client.client.app_key == {"app_key": "test_token"}

    def test_backward_compatibility_without_args(self) -> None:
        """Test backward compatibility - Client can still be created without arguments."""
        client = Client()
        assert client.client.app_key is None


class TestBuildSystemCopiesHTTPBackends:
    """Tests to verify the build system copies HTTP backend files correctly."""

    def test_py_typed_marker_exists(self) -> None:
        """Test that py.typed marker file exists for PEP 561 compliance."""
        import pydantic_tfl_api

        package_dir = Path(pydantic_tfl_api.__file__).parent
        py_typed_path = package_dir / "py.typed"
        assert py_typed_path.exists(), f"py.typed marker file should exist at {py_typed_path}"

    def test_http_client_base_importable_from_core(self) -> None:
        """Test that HTTPClientBase can be imported from core."""
        from pydantic_tfl_api.core import HTTPClientBase

        assert HTTPClientBase is not None

    def test_unified_response_importable_from_core(self) -> None:
        """Test that UnifiedResponse can be imported from core."""
        from pydantic_tfl_api.core import UnifiedResponse

        assert UnifiedResponse is not None
