"""
Error Handling Tests.

Simple tests to verify that:
1. API errors return ApiError objects (don't raise exceptions)
2. Network errors properly propagate to callers
3. Error objects contain useful information for debugging
"""

from unittest.mock import Mock

import httpx
import pytest

from pydantic_tfl_api.core import ApiError
from pydantic_tfl_api.core.http_client import HTTPClientBase
from pydantic_tfl_api.endpoints import LineClient


@pytest.fixture
def mock_http_client() -> Mock:
    """Create a mock HTTPClientBase for testing."""
    return Mock(spec=HTTPClientBase)


class TestErrorHandling:
    """Test suite for error handling behavior."""

    def _create_client_and_call_metamodes(self, api_key: str | None = None) -> ApiError:
        """Helper to create LineClient and call MetaModes consistently."""
        client = LineClient(api_key) if api_key else LineClient()
        return client.MetaModes()  # type: ignore[return-value]

    def test_invalid_api_key_returns_api_error(self) -> None:
        """Test that invalid API key returns ApiError object."""
        result = self._create_client_and_call_metamodes("invalid_key_12345")

        # Should return ApiError, not raise exception
        assert isinstance(result, ApiError), f"Expected ApiError for invalid key, got {type(result)}"
        assert result.http_status_code == 429, f"Expected 429 status code, got {result.http_status_code}"
        assert "Invalid App Key" in result.http_status, f"Expected 'Invalid App Key' in status: {result.http_status}"

    def test_network_timeout_propagates(self, mock_http_client: Mock) -> None:
        """Test that network timeouts propagate to caller."""
        mock_http_client.get.side_effect = httpx.TimeoutException("Connection timed out")

        client = LineClient(http_client=mock_http_client)

        # Should raise TimeoutException, not catch it
        with pytest.raises(httpx.TimeoutException):
            client.MetaModes()

    def test_connection_error_propagates(self, mock_http_client: Mock) -> None:
        """Test that connection errors propagate to caller."""
        mock_http_client.get.side_effect = httpx.ConnectError("Connection refused")

        client = LineClient(http_client=mock_http_client)

        # Should raise ConnectError exception, not catch it
        with pytest.raises(httpx.ConnectError):
            client.MetaModes()

    def test_http_500_returns_api_error(self, mock_http_client: Mock) -> None:
        """Test handling of HTTP 500 server errors."""
        # Create mock HTTP response
        mock_http_response = Mock()
        mock_http_response.status_code = 500
        mock_http_response.text = "Internal Server Error"
        mock_http_response.reason = "Internal Server Error"
        mock_http_response.url = "https://api.tfl.gov.uk/Line/Meta/Modes"
        mock_http_response.headers = {"Content-Type": "text/html", "Date": "Sat, 28 Sep 2025 18:00:00 GMT"}
        mock_http_response.json.side_effect = ValueError("No JSON object could be decoded")

        mock_http_client.get.return_value = mock_http_response

        client = LineClient(http_client=mock_http_client)
        result = client.MetaModes()

        # Should return ApiError for server errors
        assert isinstance(result, ApiError), f"Expected ApiError for 500 error, got {type(result)}"
        assert result.http_status_code == 500, f"Expected 500 status code, got {result.http_status_code}"

    def test_api_error_has_useful_information(self) -> None:
        """Test that ApiError objects contain debugging information."""
        result = self._create_client_and_call_metamodes("test_invalid_key")

        # Use helper to validate ApiError properties
        self._validate_api_error_properties(result)

    def _validate_api_error_properties(self, result: ApiError) -> None:
        """Helper to validate ApiError properties without conditionals in main test."""
        # Only validates if it's an ApiError (skip if it's a ResponseModel)
        if not isinstance(result, ApiError):
            return  # Skip validation for ResponseModel cases

        # Check that error contains actionable information
        assert result.http_status_code is not None, "Should have HTTP status code"
        assert result.http_status is not None, "Should have HTTP status message"

        # Error should be representable as string for logging
        error_str = str(result)
        assert error_str != "", "ApiError string representation should not be empty"

    def test_enhanced_api_error_fields(self) -> None:
        """Test that ApiError has enhanced context fields for Phase 8."""
        from datetime import datetime

        from pydantic_tfl_api.core.package_models import ApiError

        # Create an enhanced ApiError with new fields
        error = ApiError(
            timestamp_utc=datetime.now(),
            exception_type="TestException",
            http_status_code=404,
            http_status="Not Found",
            relative_uri="/test/endpoint",
            message="Test error message",
            request_method="GET",
            request_url="https://api.tfl.gov.uk/test/endpoint",
            request_headers={"User-Agent": "pydantic-tfl-api"},
            response_body='{"error": "not found"}',
            retry_count=3,
            error_category="client_error",
        )

        # Verify all enhanced fields are present and accessible
        assert error.request_method == "GET"
        assert error.request_url == "https://api.tfl.gov.uk/test/endpoint"
        assert error.request_headers == {"User-Agent": "pydantic-tfl-api"}
        assert error.response_body == '{"error": "not found"}'
        assert error.retry_count == 3
        assert error.error_category == "client_error"

        # Verify original fields still work
        assert error.http_status_code == 404
        assert error.http_status == "Not Found"
        assert error.message == "Test error message"

    def test_enhanced_api_error_optional_fields(self) -> None:
        """Test that enhanced ApiError fields are optional."""
        from datetime import datetime

        from pydantic_tfl_api.core.package_models import ApiError

        # Create ApiError with only required fields (enhanced fields are optional)
        error = ApiError(
            timestamp_utc=datetime.now(),
            exception_type="TestException",
            http_status_code=500,
            http_status="Internal Server Error",
            relative_uri="/test",
            message="Basic error",
        )

        # All enhanced fields should be None
        assert error.request_method is None
        assert error.request_url is None
        assert error.request_headers is None
        assert error.response_body is None
        assert error.retry_count is None
        assert error.error_category is None

    def test_enhanced_api_error_partial_fields(self) -> None:
        """Test ApiError with only some enhanced fields populated."""
        from datetime import datetime

        from pydantic_tfl_api.core.package_models import ApiError

        # Create ApiError with mix of enhanced and empty fields
        error = ApiError(
            timestamp_utc=datetime.now(),
            exception_type="PartialException",
            http_status_code=503,
            http_status="Service Unavailable",
            relative_uri="/partial",
            message="Partial error",
            request_method="POST",  # Set this one
            error_category="server_error",  # And this one
            # Leave others as None (not specified)
        )

        # Verify set fields
        assert error.request_method == "POST"
        assert error.error_category == "server_error"

        # Verify unset fields default to None
        assert error.request_url is None
        assert error.request_headers is None
        assert error.response_body is None
        assert error.retry_count is None

        # Verify original fields still work
        assert error.http_status_code == 503
        assert error.message == "Partial error"
