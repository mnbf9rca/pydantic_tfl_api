# Requests-based HTTP Client Implementation
# This module provides an HTTP client implementation using the requests library.

from collections.abc import Mapping
from typing import Any

import requests
from requests import Response

from ..http_client import HTTPClientBase, HTTPResponse


class RequestsResponse:
    """Wrapper around requests.Response to ensure HTTPResponse protocol compliance.

    This class wraps a requests.Response object to provide a consistent interface
    that matches the HTTPResponse protocol. While requests.Response already has
    most of these properties, this wrapper ensures type consistency and allows
    for any necessary adaptations.
    """

    def __init__(self, response: Response) -> None:
        self._response = response

    @property
    def status_code(self) -> int:
        """HTTP status code of the response."""
        return self._response.status_code

    @property
    def headers(self) -> Mapping[str, str]:
        """Response headers as a case-insensitive mapping."""
        # Return original CaseInsensitiveDict which is case-insensitive
        return self._response.headers

    @property
    def text(self) -> str:
        """Response body as text."""
        return self._response.text

    @property
    def url(self) -> str:
        """The URL of the request."""
        return str(self._response.url)

    @property
    def reason(self) -> str:
        """HTTP reason phrase (e.g., 'OK', 'Not Found')."""
        return self._response.reason or ""

    def json(self) -> Any:
        """Parse response body as JSON."""
        return self._response.json()

    def raise_for_status(self) -> None:
        """Raise an exception if the response indicates an error."""
        self._response.raise_for_status()


class RequestsClient(HTTPClientBase):
    """HTTP client implementation using the requests library.

    This is the default HTTP client for the library, providing synchronous
    HTTP requests using the popular requests library.
    """

    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> HTTPResponse:
        """Send a GET request using the requests library.

        Args:
            url: The URL to send the request to (should include query parameters).
            headers: Optional headers to include in the request.
            timeout: Request timeout in seconds. Defaults to 30 if not specified.

        Returns:
            A RequestsResponse object wrapping the requests.Response.
        """
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout if timeout is not None else 30,
        )
        return RequestsResponse(response)
