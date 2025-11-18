"""Tests for the requests HTTP backend implementation.

These tests are specific to the requests library backend and will be
skipped if requests is not installed.
"""

from unittest.mock import Mock, patch

import pytest

# Skip this module if requests is not installed
requests = pytest.importorskip("requests")

from pydantic_tfl_api.core import HTTPResponse  # noqa: E402
from pydantic_tfl_api.core.http_backends.requests_client import RequestsClient, RequestsResponse  # noqa: E402


class TestRequestsResponseConformsToProtocol:
    """Tests for the HTTPResponse protocol conformance."""

    def test_requests_response_conforms_to_protocol(self) -> None:
        """Test that RequestsResponse conforms to HTTPResponse protocol."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = "test"
        mock_response.url = "http://test.com"
        mock_response.reason = "OK"
        mock_response.json.return_value = {"key": "value"}

        response = RequestsResponse(mock_response)
        assert isinstance(response, HTTPResponse)


class TestRequestsResponse:
    """Tests for the RequestsResponse wrapper class."""

    @pytest.fixture
    def mock_requests_response(self) -> Mock:
        """Create a mock requests.Response for testing."""
        mock = Mock(spec=requests.Response)
        mock.status_code = 200
        mock.headers = {"Content-Type": "application/json", "Date": "Mon, 01 Jan 2024 00:00:00 GMT"}
        mock.text = '{"message": "success"}'
        mock.url = "http://api.tfl.gov.uk/Line/victoria"
        mock.reason = "OK"
        mock.json.return_value = {"message": "success"}
        return mock

    def test_status_code(self, mock_requests_response: Mock) -> None:
        """Test status_code property."""
        response = RequestsResponse(mock_requests_response)
        assert response.status_code == 200

    def test_headers(self, mock_requests_response: Mock) -> None:
        """Test headers property returns dict."""
        response = RequestsResponse(mock_requests_response)
        headers = response.headers
        assert isinstance(headers, dict)
        assert headers["Content-Type"] == "application/json"

    def test_text(self, mock_requests_response: Mock) -> None:
        """Test text property."""
        response = RequestsResponse(mock_requests_response)
        assert response.text == '{"message": "success"}'

    def test_url(self, mock_requests_response: Mock) -> None:
        """Test url property."""
        response = RequestsResponse(mock_requests_response)
        assert response.url == "http://api.tfl.gov.uk/Line/victoria"

    def test_reason(self, mock_requests_response: Mock) -> None:
        """Test reason property."""
        response = RequestsResponse(mock_requests_response)
        assert response.reason == "OK"

    def test_reason_empty(self) -> None:
        """Test reason property returns empty string when None."""
        mock = Mock(spec=requests.Response)
        mock.reason = None
        response = RequestsResponse(mock)
        assert response.reason == ""

    def test_json(self, mock_requests_response: Mock) -> None:
        """Test json method."""
        response = RequestsResponse(mock_requests_response)
        data = response.json()
        assert data == {"message": "success"}

    def test_raise_for_status(self, mock_requests_response: Mock) -> None:
        """Test raise_for_status delegates to underlying response."""
        response = RequestsResponse(mock_requests_response)
        response.raise_for_status()
        mock_requests_response.raise_for_status.assert_called_once()


class TestRequestsClient:
    """Tests for the RequestsClient implementation."""

    def test_get_makes_request(self) -> None:
        """Test that get method makes a GET request."""
        with patch("pydantic_tfl_api.core.http_backends.requests_client.requests.get") as mock_get:
            mock_response = Mock(spec=requests.Response)
            mock_get.return_value = mock_response

            client = RequestsClient()
            result = client.get("http://test.com", headers={"Accept": "application/json"}, timeout=60)

            mock_get.assert_called_once_with("http://test.com", headers={"Accept": "application/json"}, timeout=60)
            assert isinstance(result, RequestsResponse)

    def test_get_default_timeout(self) -> None:
        """Test that get method uses default timeout of 30 seconds."""
        with patch("pydantic_tfl_api.core.http_backends.requests_client.requests.get") as mock_get:
            mock_response = Mock(spec=requests.Response)
            mock_get.return_value = mock_response

            client = RequestsClient()
            client.get("http://test.com")

            mock_get.assert_called_once_with("http://test.com", headers=None, timeout=30)


class TestRequestsClientImports:
    """Tests for requests client imports."""

    def test_http_backends_module_has_requests_client(self) -> None:
        """Test that http_backends module has RequestsClient."""
        from pydantic_tfl_api.core import http_backends

        assert hasattr(http_backends, "RequestsClient")

    def test_requests_client_importable_from_core(self) -> None:
        """Test that RequestsClient can be imported from core."""
        from pydantic_tfl_api.core import RequestsClient

        assert RequestsClient is not None
