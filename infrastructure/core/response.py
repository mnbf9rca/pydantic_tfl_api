# Unified Response Wrapper
# This module provides a unified response wrapper for consistency across HTTP clients.

from collections.abc import Mapping
from typing import Any

from .http_client import HTTPResponse


class UnifiedResponse:
    """Unified response wrapper providing a consistent interface across HTTP clients.

    This class wraps any HTTPResponse-conforming object to provide a normalized
    interface for response handling. It serves as the primary response type used
    throughout the library, abstracting away differences between HTTP client
    implementations.

    The wrapper delegates to the underlying response for basic properties while
    providing additional utility methods and ensuring consistent behavior.
    """

    def __init__(self, response: HTTPResponse) -> None:
        """Initialize the unified response wrapper.

        Args:
            response: An object conforming to the HTTPResponse protocol.
        """
        self._response = response

    @property
    def status_code(self) -> int:
        """HTTP status code of the response."""
        return self._response.status_code

    @property
    def headers(self) -> Mapping[str, str]:
        """Response headers as a case-insensitive mapping."""
        return self._response.headers

    @property
    def text(self) -> str:
        """Response body as text."""
        return self._response.text

    @property
    def url(self) -> str:
        """The URL of the request."""
        return self._response.url

    @property
    def reason(self) -> str:
        """HTTP reason phrase (e.g., 'OK', 'Not Found')."""
        return self._response.reason

    def json(self) -> Any:
        """Parse response body as JSON.

        Returns:
            The parsed JSON data.

        Raises:
            JSONDecodeError: If the response body is not valid JSON.
        """
        return self._response.json()

    def raise_for_status(self) -> None:
        """Raise an exception if the response indicates an error.

        Raises:
            HTTPError: If the response status code indicates an error (4xx or 5xx).
        """
        self._response.raise_for_status()

    @property
    def ok(self) -> bool:
        """Check if the response was successful (status code < 400)."""
        return self.status_code < 400

    @property
    def is_error(self) -> bool:
        """Check if the response indicates an error (status code >= 400)."""
        return self.status_code >= 400

    @property
    def is_client_error(self) -> bool:
        """Check if the response indicates a client error (4xx status code)."""
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        """Check if the response indicates a server error (5xx status code)."""
        return 500 <= self.status_code < 600
