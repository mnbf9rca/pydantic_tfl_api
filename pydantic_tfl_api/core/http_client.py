# HTTP Client Abstraction Layer
# This module provides the base abstractions for HTTP clients, allowing
# the library to support multiple HTTP backends (requests, httpx, etc.)

from abc import ABC, abstractmethod
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
    def headers(self) -> dict[str, str]:
        """Response headers as a dictionary."""
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
        params: dict[str, Any] | None = None,
        timeout: int | None = None,
    ) -> HTTPResponse:
        """Send a GET request.

        Args:
            url: The URL to send the request to.
            headers: Optional headers to include in the request.
            params: Optional query parameters (not used directly, URL should include params).
            timeout: Request timeout in seconds.

        Returns:
            An HTTPResponse object containing the response data.
        """
        ...
