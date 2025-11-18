"""Tests for httpx support and async client functionality (Phase 2)."""

from collections.abc import Mapping
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from pydantic_tfl_api.core import (
    AsyncClient,
    AsyncHTTPClientBase,
    AsyncRestClient,
    get_default_async_http_client,
    get_default_http_client,
)
from pydantic_tfl_api.core.http_backends.async_httpx_client import AsyncHttpxClient, AsyncHttpxResponse
from pydantic_tfl_api.core.http_backends.httpx_client import HttpxClient, HttpxResponse
from pydantic_tfl_api.core.http_client import HTTPResponse


class TestAsyncHTTPClientBase:
    """Tests for the AsyncHTTPClientBase abstract class."""

    def test_cannot_instantiate_directly(self) -> None:
        """Test that AsyncHTTPClientBase cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            AsyncHTTPClientBase()  # type: ignore[abstract]

    def test_subclass_must_implement_get(self) -> None:
        """Test that subclasses must implement the get method."""

        class IncompleteAsyncClient(AsyncHTTPClientBase):
            pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteAsyncClient()  # type: ignore[abstract]


class TestHttpxResponse:
    """Tests for the HttpxResponse wrapper class."""

    @pytest.fixture
    def mock_httpx_response(self) -> Mock:
        """Create a mock httpx.Response for testing."""
        mock = Mock(spec=httpx.Response)
        mock.status_code = 200
        mock.headers = httpx.Headers({"Content-Type": "application/json", "Date": "Mon, 01 Jan 2024 00:00:00 GMT"})
        mock.text = '{"message": "success"}'
        mock.url = httpx.URL("http://api.tfl.gov.uk/Line/victoria")
        mock.reason_phrase = "OK"
        mock.json.return_value = {"message": "success"}
        return mock

    def test_conforms_to_protocol(self, mock_httpx_response: Mock) -> None:
        """Test that HttpxResponse conforms to HTTPResponse protocol."""
        response = HttpxResponse(mock_httpx_response)
        assert isinstance(response, HTTPResponse)

    def test_status_code(self, mock_httpx_response: Mock) -> None:
        """Test status_code property."""
        response = HttpxResponse(mock_httpx_response)
        assert response.status_code == 200

    def test_headers(self, mock_httpx_response: Mock) -> None:
        """Test headers property returns dict."""
        response = HttpxResponse(mock_httpx_response)
        headers = response.headers
        # Headers should be a case-insensitive Mapping (httpx.Headers)
        assert isinstance(headers, Mapping)
        assert headers["content-type"] == "application/json"
        # Verify case-insensitivity
        assert headers["Content-Type"] == "application/json"

    def test_text(self, mock_httpx_response: Mock) -> None:
        """Test text property."""
        response = HttpxResponse(mock_httpx_response)
        assert response.text == '{"message": "success"}'

    def test_url(self, mock_httpx_response: Mock) -> None:
        """Test url property."""
        response = HttpxResponse(mock_httpx_response)
        assert response.url == "http://api.tfl.gov.uk/Line/victoria"

    def test_reason(self, mock_httpx_response: Mock) -> None:
        """Test reason property."""
        response = HttpxResponse(mock_httpx_response)
        assert response.reason == "OK"

    def test_reason_empty(self) -> None:
        """Test reason property returns empty string when None."""
        mock = Mock(spec=httpx.Response)
        mock.reason_phrase = None
        response = HttpxResponse(mock)
        assert response.reason == ""

    def test_json(self, mock_httpx_response: Mock) -> None:
        """Test json method."""
        response = HttpxResponse(mock_httpx_response)
        data = response.json()
        assert data == {"message": "success"}

    def test_raise_for_status(self, mock_httpx_response: Mock) -> None:
        """Test raise_for_status delegates to underlying response."""
        response = HttpxResponse(mock_httpx_response)
        response.raise_for_status()
        mock_httpx_response.raise_for_status.assert_called_once()


class TestHttpxClient:
    """Tests for the HttpxClient implementation."""

    def test_get_makes_request(self) -> None:
        """Test that get method makes a GET request."""
        with patch("pydantic_tfl_api.core.http_backends.httpx_client.httpx.get") as mock_get:
            mock_response = Mock(spec=httpx.Response)
            mock_get.return_value = mock_response

            client = HttpxClient()
            result = client.get("http://test.com", headers={"Accept": "application/json"}, timeout=60)

            mock_get.assert_called_once_with("http://test.com", headers={"Accept": "application/json"}, timeout=60)
            assert isinstance(result, HttpxResponse)

    def test_get_default_timeout(self) -> None:
        """Test that get method uses default timeout of 30 seconds."""
        with patch("pydantic_tfl_api.core.http_backends.httpx_client.httpx.get") as mock_get:
            mock_response = Mock(spec=httpx.Response)
            mock_get.return_value = mock_response

            client = HttpxClient()
            client.get("http://test.com")

            mock_get.assert_called_once_with("http://test.com", headers=None, timeout=30)


class TestAsyncHttpxResponse:
    """Tests for the AsyncHttpxResponse wrapper class."""

    @pytest.fixture
    def mock_httpx_response(self) -> Mock:
        """Create a mock httpx.Response for testing."""
        mock = Mock(spec=httpx.Response)
        mock.status_code = 200
        mock.headers = httpx.Headers({"Content-Type": "application/json"})
        mock.text = '{"data": "test"}'
        mock.url = httpx.URL("http://api.tfl.gov.uk/test")
        mock.reason_phrase = "OK"
        mock.json.return_value = {"data": "test"}
        return mock

    def test_conforms_to_protocol(self, mock_httpx_response: Mock) -> None:
        """Test that AsyncHttpxResponse conforms to HTTPResponse protocol."""
        response = AsyncHttpxResponse(mock_httpx_response)
        assert isinstance(response, HTTPResponse)

    def test_status_code(self, mock_httpx_response: Mock) -> None:
        """Test status_code property."""
        response = AsyncHttpxResponse(mock_httpx_response)
        assert response.status_code == 200

    def test_headers(self, mock_httpx_response: Mock) -> None:
        """Test headers property returns dict."""
        response = AsyncHttpxResponse(mock_httpx_response)
        headers = response.headers
        # Headers should be a case-insensitive Mapping (httpx.Headers)
        assert isinstance(headers, Mapping)
        # Verify case-insensitivity
        assert headers["Content-Type"] == "application/json"

    def test_text(self, mock_httpx_response: Mock) -> None:
        """Test text property."""
        response = AsyncHttpxResponse(mock_httpx_response)
        assert response.text == '{"data": "test"}'

    def test_url(self, mock_httpx_response: Mock) -> None:
        """Test url property."""
        response = AsyncHttpxResponse(mock_httpx_response)
        assert response.url == "http://api.tfl.gov.uk/test"

    def test_reason(self, mock_httpx_response: Mock) -> None:
        """Test reason property."""
        response = AsyncHttpxResponse(mock_httpx_response)
        assert response.reason == "OK"

    def test_reason_empty(self) -> None:
        """Test reason property returns empty string when None."""
        mock = Mock(spec=httpx.Response)
        mock.reason_phrase = None
        response = AsyncHttpxResponse(mock)
        assert response.reason == ""

    def test_json(self, mock_httpx_response: Mock) -> None:
        """Test json method."""
        response = AsyncHttpxResponse(mock_httpx_response)
        data = response.json()
        assert data == {"data": "test"}

    def test_raise_for_status(self, mock_httpx_response: Mock) -> None:
        """Test raise_for_status delegates to underlying response."""
        response = AsyncHttpxResponse(mock_httpx_response)
        response.raise_for_status()
        mock_httpx_response.raise_for_status.assert_called_once()


class TestAsyncHttpxClient:
    """Tests for the AsyncHttpxClient implementation."""

    @pytest.mark.asyncio
    async def test_get_makes_async_request(self) -> None:
        """Test that get method makes an async GET request."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.headers = httpx.Headers({})
        mock_response.text = "{}"
        mock_response.url = httpx.URL("http://test.com")
        mock_response.reason_phrase = "OK"

        with patch("pydantic_tfl_api.core.http_backends.async_httpx_client.httpx.AsyncClient") as mock_async_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_async_client.return_value.__aenter__.return_value = mock_client_instance

            client = AsyncHttpxClient()
            result = await client.get("http://test.com", headers={"Accept": "application/json"}, timeout=60)

            mock_client_instance.get.assert_called_once_with(
                "http://test.com", headers={"Accept": "application/json"}, timeout=60
            )
            assert isinstance(result, AsyncHttpxResponse)

    @pytest.mark.asyncio
    async def test_get_default_timeout(self) -> None:
        """Test that get method uses default timeout of 30 seconds."""
        mock_response = Mock(spec=httpx.Response)

        with patch("pydantic_tfl_api.core.http_backends.async_httpx_client.httpx.AsyncClient") as mock_async_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_async_client.return_value.__aenter__.return_value = mock_client_instance

            client = AsyncHttpxClient()
            await client.get("http://test.com")

            mock_client_instance.get.assert_called_once_with("http://test.com", headers=None, timeout=30)


class TestGetDefaultHttpClient:
    """Tests for the get_default_http_client factory function."""

    def test_returns_httpx_client_when_available(self) -> None:
        """Test that httpx client is returned when httpx is available."""
        client = get_default_http_client()
        # With httpx installed in dev dependencies, it should return HttpxClient
        assert isinstance(client, HttpxClient)

    def test_fallback_to_requests(self) -> None:
        """Test that the auto-detection prefers httpx but can fall back to requests.

        This test validates the design - in practice httpx is always available in tests.
        We verify the function exists and returns the right type when httpx is available.
        """
        # Since httpx is installed in dev dependencies, this will return HttpxClient
        client = get_default_http_client()

        # Verify it returns the preferred httpx client
        assert isinstance(client, HttpxClient)

        # Also verify that RequestsClient is importable as a fallback option
        # (only when requests is installed)
        from contextlib import suppress

        with suppress(ImportError):
            from pydantic_tfl_api.core.http_backends.requests_client import RequestsClient

            assert RequestsClient is not None


class TestGetDefaultAsyncHttpClient:
    """Tests for the get_default_async_http_client factory function."""

    def test_returns_async_httpx_client(self) -> None:
        """Test that async httpx client is returned."""
        client = get_default_async_http_client()
        assert isinstance(client, AsyncHttpxClient)


class TestAsyncRestClient:
    """Tests for AsyncRestClient."""

    def test_default_http_client(self) -> None:
        """Test that AsyncRestClient uses AsyncHttpxClient by default."""
        client = AsyncRestClient()
        assert isinstance(client.http_client, AsyncHttpxClient)

    def test_custom_http_client_injection(self) -> None:
        """Test that a custom async HTTP client can be injected."""

        class CustomAsyncClient(AsyncHTTPClientBase):
            async def get(
                self,
                url: str,
                headers: dict[str, str] | None = None,
                timeout: int | None = None,
            ) -> HTTPResponse:
                mock = Mock()
                mock.status_code = 200
                return mock

        custom_client = CustomAsyncClient()
        rest_client = AsyncRestClient(http_client=custom_client)
        assert rest_client.http_client is custom_client

    def test_app_key_set_correctly(self) -> None:
        """Test that app_key is set correctly."""
        client = AsyncRestClient(app_key="test_key")
        assert client.app_key == {"app_key": "test_key"}

    def test_app_key_none_when_not_provided(self) -> None:
        """Test that app_key is None when not provided."""
        client = AsyncRestClient()
        assert client.app_key is None

    @pytest.mark.asyncio
    async def test_send_request_builds_correct_url(self) -> None:
        """Test that send_request builds the correct URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "{}"
        mock_response.url = "http://api.tfl.gov.uk/Line/victoria"
        mock_response.reason = "OK"

        mock_client = AsyncMock(spec=AsyncHTTPClientBase)
        mock_client.get.return_value = mock_response

        rest_client = AsyncRestClient(http_client=mock_client)
        await rest_client.send_request("http://api.tfl.gov.uk/", "Line/victoria")

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        url = call_args[0][0] if call_args[0] else call_args.kwargs.get("url")
        assert "Line/victoria" in url

    @pytest.mark.asyncio
    async def test_send_request_includes_app_key(self) -> None:
        """Test that app_key is included in request headers."""
        mock_response = Mock()
        mock_response.status_code = 200

        mock_client = AsyncMock(spec=AsyncHTTPClientBase)
        mock_client.get.return_value = mock_response

        rest_client = AsyncRestClient(app_key="test_key", http_client=mock_client)
        await rest_client.send_request("http://api.tfl.gov.uk/", "Line/victoria")

        call_args = mock_client.get.call_args
        headers = call_args.kwargs.get("headers") or call_args[1].get("headers")
        assert headers["app_key"] == "test_key"

    def test_get_query_strings_with_none_values(self) -> None:
        """Test that None values are excluded from query strings."""
        client = AsyncRestClient()
        result = client._get_query_strings({"a": "1", "b": None, "c": "3"})
        assert "a=1" in result
        assert "c=3" in result
        assert "b=" not in result

    def test_get_query_strings_empty(self) -> None:
        """Test query strings with empty params."""
        client = AsyncRestClient()
        result = client._get_query_strings(None)
        assert result == ""


class TestAsyncClient:
    """Tests for AsyncClient base class."""

    def test_default_client_works(self) -> None:
        """Test that AsyncClient works with default HTTP client."""
        client = AsyncClient()
        assert isinstance(client.client.http_client, AsyncHttpxClient)

    def test_custom_http_client_passed_through(self) -> None:
        """Test that custom HTTP client is passed to AsyncRestClient."""

        class MockAsyncHTTPClient(AsyncHTTPClientBase):
            async def get(
                self,
                url: str,
                headers: dict[str, str] | None = None,
                timeout: int | None = None,
            ) -> HTTPResponse:
                mock = Mock()
                mock.status_code = 200
                return mock

        mock_client = MockAsyncHTTPClient()
        client = AsyncClient(http_client=mock_client)
        assert client.client.http_client is mock_client

    def test_api_token_set_correctly(self) -> None:
        """Test that api_token is passed to AsyncRestClient."""
        client = AsyncClient("test_token")
        assert client.client.app_key == {"app_key": "test_token"}

    def test_models_loaded(self) -> None:
        """Test that models are loaded correctly."""
        client = AsyncClient()
        assert len(client.models) > 0
        assert "ApiError" in client.models

    def test_get_model_raises_for_unknown(self) -> None:
        """Test that _get_model raises ValueError for unknown model."""
        client = AsyncClient()
        with pytest.raises(ValueError, match="No model found"):
            client._get_model("NonExistentModel")

    def test_parse_int_or_none_valid(self) -> None:
        """Test _parse_int_or_none with valid int."""
        result = AsyncClient._parse_int_or_none("123")
        assert result == 123

    def test_parse_int_or_none_invalid(self) -> None:
        """Test _parse_int_or_none with invalid value."""
        result = AsyncClient._parse_int_or_none("not_a_number")
        assert result is None

    def test_parse_int_or_none_empty(self) -> None:
        """Test _parse_int_or_none with empty string."""
        result = AsyncClient._parse_int_or_none("")
        assert result is None


class TestImports:
    """Tests to verify that all new classes are properly importable."""

    def test_httpx_client_importable_from_core(self) -> None:
        """Test that HttpxClient can be imported from core."""
        from pydantic_tfl_api.core import http_backends

        assert hasattr(http_backends, "HttpxClient")

    def test_async_httpx_client_importable_from_core(self) -> None:
        """Test that AsyncHttpxClient can be imported from core."""
        from pydantic_tfl_api.core import http_backends

        assert hasattr(http_backends, "AsyncHttpxClient")

    def test_async_client_importable_from_core(self) -> None:
        """Test that AsyncClient can be imported from core."""
        from pydantic_tfl_api.core import AsyncClient

        assert AsyncClient is not None

    def test_async_rest_client_importable_from_core(self) -> None:
        """Test that AsyncRestClient can be imported from core."""
        from pydantic_tfl_api.core import AsyncRestClient

        assert AsyncRestClient is not None

    def test_async_http_client_base_importable_from_core(self) -> None:
        """Test that AsyncHTTPClientBase can be imported from core."""
        from pydantic_tfl_api.core import AsyncHTTPClientBase

        assert AsyncHTTPClientBase is not None

    def test_factory_functions_importable(self) -> None:
        """Test that factory functions can be imported from core."""
        from pydantic_tfl_api.core import get_default_async_http_client, get_default_http_client

        assert get_default_http_client is not None
        assert get_default_async_http_client is not None


class TestImportErrorHandling:
    """Tests for import error handling when optional dependencies are missing."""

    def test_get_default_async_http_client_raises_helpful_error_when_httpx_missing(self) -> None:
        """Test that get_default_async_http_client raises helpful error when httpx not installed."""
        import builtins
        import sys

        original_import = builtins.__import__

        def mock_import(name: str, *args: object, **kwargs: object) -> object:
            if "async_httpx_client" in name:
                raise ImportError("No module named 'httpx'")
            return original_import(name, *args, **kwargs)

        # Remove cached module to force reimport
        modules_to_remove = [k for k in sys.modules if "async_httpx_client" in k]
        removed = {k: sys.modules.pop(k) for k in modules_to_remove}

        try:
            with patch.object(builtins, "__import__", side_effect=mock_import):
                from pydantic_tfl_api.core.http_client import get_default_async_http_client

                with pytest.raises(ImportError) as exc_info:
                    get_default_async_http_client()

                assert "httpx is required" in str(exc_info.value)
                assert "pip install pydantic-tfl-api[httpx]" in str(exc_info.value)
        finally:
            # Restore modules
            sys.modules.update(removed)

    def test_get_default_http_client_falls_back_to_requests(self) -> None:
        """Test that get_default_http_client falls back to requests when httpx not available."""
        # Skip if requests is not installed (this test needs requests for the fallback)
        pytest.importorskip("requests")

        import builtins
        import sys

        from pydantic_tfl_api.core.http_backends.requests_client import RequestsClient

        original_import = builtins.__import__

        def mock_import(name: str, *args: object, **kwargs: object) -> object:
            if "httpx_client" in name and "async" not in name:
                raise ImportError("No module named 'httpx'")
            return original_import(name, *args, **kwargs)

        # Remove cached module to force reimport
        modules_to_remove = [k for k in sys.modules if "httpx_client" in k and "async" not in k]
        removed = {k: sys.modules.pop(k) for k in modules_to_remove}

        try:
            with patch.object(builtins, "__import__", side_effect=mock_import):
                from pydantic_tfl_api.core.http_client import get_default_http_client

                client = get_default_http_client()
                assert isinstance(client, RequestsClient)
        finally:
            # Restore modules
            sys.modules.update(removed)
