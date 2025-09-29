from .client import Client
from .package_models import ApiError, GenericResponseModel, ResponseModel
from .rest_client import RestClient

# Runtime version discovery from installed package metadata
try:
    from importlib.metadata import version

    __version__ = version("pydantic_tfl_api")
except Exception:
    # Fallback for development or if package not properly installed
    __version__ = "unknown"

__all__ = ["ApiError", "ResponseModel", "GenericResponseModel", "Client", "RestClient", "__version__"]
