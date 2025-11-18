# HTTP Client Abstraction Layer
# This module provides the base abstractions for HTTP clients, allowing
# the library to support multiple HTTP backends (requests, httpx, etc.)

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class HTTPResponse(Protocol):
    """Protocol defining the interface for HTTP responses.

    This protocol ensures that any HTTP client implementation provides
    a consistent interface for accessing response data, regardless of
    the underlying HTTP library being used.
    """

    @property
    def status_code(self) -> int:
        """HTTP status code of the response."""
        ...

    @property
    def headers(self) -> Mapping[str, str]:
        """Response headers as a case-insensitive mapping."""
        ...

    @property
    def text(self) -> str:
        """Response body as text."""
        ...

    @property
    def url(self) -> str:
        """The URL of the request."""
        ...

    @property
    def reason(self) -> str:
        """HTTP reason phrase (e.g., 'OK', 'Not Found')."""
        ...

    def json(self) -> Any:
        """Parse response body as JSON."""
        ...

    def raise_for_status(self) -> None:
        """Raise an exception if the response indicates an error."""
        ...


class HTTPClientBase(ABC):
    """Abstract base class for HTTP clients.

    This class defines the interface that all HTTP client implementations
    must follow. It uses sync methods for Phase 1, with async variants
    to be added in Phase 2.
    """

    @abstractmethod
    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> HTTPResponse:
        """Send a GET request.

        Args:
            url: The URL to send the request to (should include query parameters).
            headers: Optional headers to include in the request.
            timeout: Request timeout in seconds.

        Returns:
            An HTTPResponse object containing the response data.
        """
        ...


class AsyncHTTPClientBase(ABC):
    """Abstract base class for asynchronous HTTP clients.

    This class defines the interface that all async HTTP client implementations
    must follow. It provides async variants of HTTP methods for use with
    asyncio-based applications.
    """

    @abstractmethod
    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> HTTPResponse:
        """Send an async GET request.

        Args:
            url: The URL to send the request to (should include query parameters).
            headers: Optional headers to include in the request.
            timeout: Request timeout in seconds.

        Returns:
            An HTTPResponse object containing the response data.
        """
        ...


def get_default_http_client() -> HTTPClientBase:
    """Get the default HTTP client implementation.

    Tries to use httpx if available (better performance), otherwise falls back
    to requests.

    Returns:
        An HTTPClientBase implementation.
    """
    try:
        from .http_backends.httpx_client import HttpxClient

        return HttpxClient()
    except ImportError:
        from .http_backends.requests_client import RequestsClient

        return RequestsClient()


def get_default_async_http_client() -> AsyncHTTPClientBase:
    """Get the default async HTTP client implementation.

    Returns the async httpx client for use with asyncio.

    Returns:
        An AsyncHTTPClientBase implementation.

    Raises:
        ImportError: If httpx is not installed.
    """
    try:
        from .http_backends.async_httpx_client import AsyncHttpxClient

        return AsyncHttpxClient()
    except ImportError:
        raise ImportError(
            "httpx is required for async client support. "
            "Install it with: pip install pydantic-tfl-api[httpx]"
        ) from None
