from .async_client import AsyncClient
from .async_rest_client import AsyncRestClient
from .client import Client
from .http_backends import RequestsClient
from .http_client import (
    AsyncHTTPClientBase,
    HTTPClientBase,
    HTTPResponse,
    get_default_async_http_client,
    get_default_http_client,
)
from .package_models import ApiError, GenericResponseModel, ResponseModel
from .response import UnifiedResponse
from .rest_client import RestClient

# Optional httpx imports - only available if httpx is installed
try:
    from .http_backends import AsyncHttpxClient, HttpxClient  # noqa: F401

    _httpx_available = True
except ImportError:
    _httpx_available = False

# Runtime version discovery from installed package metadata
try:
    from importlib.metadata import version

    __version__ = version("pydantic_tfl_api")
except Exception:
    # Fallback for development or if package not properly installed
    __version__ = "unknown"

__all__ = [
    "ApiError",
    "ResponseModel",
    "GenericResponseModel",
    "Client",
    "AsyncClient",
    "RestClient",
    "AsyncRestClient",
    "HTTPClientBase",
    "AsyncHTTPClientBase",
    "HTTPResponse",
    "RequestsClient",
    "UnifiedResponse",
    "get_default_http_client",
    "get_default_async_http_client",
    "__version__",
]

# Add httpx clients to __all__ if available
if _httpx_available:
    __all__ += ["HttpxClient", "AsyncHttpxClient"]
