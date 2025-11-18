# httpx-based Async HTTP Client Implementation
# This module provides an asynchronous HTTP client implementation using the httpx library.

from collections.abc import Mapping
from typing import Any

import httpx

from ..http_client import AsyncHTTPClientBase, HTTPResponse


class AsyncHttpxResponse:
    """Wrapper around httpx.Response to ensure HTTPResponse protocol compliance for async clients.

    This class wraps an httpx.Response object to provide a consistent interface
    that matches the HTTPResponse protocol. It's identical to HttpxResponse but
    is used by the async client for clarity.
    """

    def __init__(self, response: httpx.Response) -> None:
        self._response = response

    @property
    def status_code(self) -> int:
        """HTTP status code of the response."""
        return self._response.status_code

    @property
    def headers(self) -> Mapping[str, str]:
        """Response headers as a case-insensitive mapping."""
        # Return original httpx.Headers which is case-insensitive
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
        return self._response.reason_phrase or ""

    def json(self) -> Any:
        """Parse response body as JSON."""
        return self._response.json()

    def raise_for_status(self) -> None:
        """Raise an exception if the response indicates an error."""
        self._response.raise_for_status()


class AsyncHttpxClient(AsyncHTTPClientBase):
    """Asynchronous HTTP client implementation using the httpx library.

    This HTTP client provides async HTTP requests using httpx,
    enabling high-performance concurrent API calls.
    """

    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> HTTPResponse:
        """Send an async GET request using the httpx library.

        Args:
            url: The URL to send the request to (should include query parameters).
            headers: Optional headers to include in the request.
            timeout: Request timeout in seconds. Defaults to 30 if not specified.

        Returns:
            An AsyncHttpxResponse object wrapping the httpx.Response.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
                timeout=timeout if timeout is not None else 30,
            )
            return AsyncHttpxResponse(response)
