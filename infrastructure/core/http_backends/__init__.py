# HTTP Backend Implementations
# This package contains concrete HTTP client implementations.

from .requests_client import RequestsClient

# Optional httpx imports - only available if httpx is installed
try:
    from .async_httpx_client import AsyncHttpxClient
    from .httpx_client import HttpxClient

    __all__ = ["RequestsClient", "HttpxClient", "AsyncHttpxClient"]
except ImportError:
    # httpx not installed, only requests backend available
    __all__ = ["RequestsClient"]
