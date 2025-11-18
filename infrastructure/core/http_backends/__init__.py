# HTTP Backend Implementations
# This package contains concrete HTTP client implementations.

from .async_httpx_client import AsyncHttpxClient
from .httpx_client import HttpxClient

# Optional requests import - only available if requests is installed
try:
    from .requests_client import RequestsClient

    __all__ = ["HttpxClient", "AsyncHttpxClient", "RequestsClient"]
except ImportError:
    # requests not installed, only httpx backends available
    __all__ = ["HttpxClient", "AsyncHttpxClient"]
