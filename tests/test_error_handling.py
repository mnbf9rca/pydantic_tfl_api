"""
Error Handling Tests.

Simple tests to verify that:
1. API errors return ApiError objects (don't raise exceptions)
2. Network errors properly propagate to callers
3. Error objects contain useful information for debugging
"""

import pytest
from unittest.mock import patch, Mock
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from pydantic_tfl_api.core import ResponseModel, ApiError
from pydantic_tfl_api.endpoints import LineClient


class TestErrorHandling:
    """Test suite for error handling behavior."""

    def test_invalid_api_key_returns_api_error(self):
        """Test that invalid API key returns ApiError object."""
        client = LineClient("invalid_key_12345")
        result = client.MetaModes()

        # Should return ApiError, not raise exception
        assert isinstance(result, ApiError), f"Expected ApiError for invalid key, got {type(result)}"
        assert result.http_status_code == 429, f"Expected 429 status code, got {result.http_status_code}"
        assert "Invalid App Key" in result.http_status, f"Expected 'Invalid App Key' in status: {result.http_status}"

    def test_network_timeout_propagates(self):
        """Test that network timeouts propagate to caller."""
        client = LineClient()

        with patch('requests.Session.request') as mock_request:
            mock_request.side_effect = Timeout("Connection timed out")

            # Should raise Timeout exception, not catch it
            with pytest.raises(Timeout):
                client.MetaModes()

    def test_connection_error_propagates(self):
        """Test that connection errors propagate to caller."""
        client = LineClient()

        with patch('requests.Session.request') as mock_request:
            mock_request.side_effect = ConnectionError("Connection refused")

            # Should raise ConnectionError exception, not catch it
            with pytest.raises(ConnectionError):
                client.MetaModes()

    def test_http_500_returns_api_error(self):
        """Test handling of HTTP 500 server errors."""
        client = LineClient()

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.reason = "Internal Server Error"
        mock_response.url = "https://api.tfl.gov.uk/Line/Meta/Modes"
        mock_response.headers = {"content-type": "text/html", "Date": "Sat, 28 Sep 2025 18:00:00 GMT"}
        mock_response.json.side_effect = ValueError("No JSON object could be decoded")

        with patch('requests.Session.request') as mock_request:
            mock_request.return_value = mock_response

            result = client.MetaModes()

            # Should return ApiError for server errors
            assert isinstance(result, ApiError), f"Expected ApiError for 500 error, got {type(result)}"
            assert result.http_status_code == 500, f"Expected 500 status code, got {result.http_status_code}"

    def test_api_error_has_useful_information(self):
        """Test that ApiError objects contain debugging information."""
        client = LineClient("test_invalid_key")
        result = client.MetaModes()

        if isinstance(result, ApiError):
            # Check that error contains actionable information
            assert result.http_status_code is not None, "Should have HTTP status code"
            assert result.http_status is not None, "Should have HTTP status message"

            # Error should be representable as string for logging
            error_str = str(result)
            assert len(error_str) > 0, "ApiError string representation should not be empty"