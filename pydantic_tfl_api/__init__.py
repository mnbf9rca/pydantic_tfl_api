from .endpoints import (
    AccidentStatsClient,
    AirQualityClient,
    BikePointClient,
    CrowdingClient,
    JourneyClient,
    LiftDisruptionsClient,
    LineClient,
    ModeClient,
    OccupancyClient,
    PlaceClient,
    RoadClient,
    SearchClient,
    StopPointClient,
    VehicleClient
)
from . import models

# Read version from package metadata (works in both development and installed package)
def _get_version():
    import logging
    logger = logging.getLogger(__name__)

    # Try importlib.metadata first (Python 3.8+)
    try:
        from importlib.metadata import version
        return version("pydantic-tfl-api")
    except ImportError:
        # Fallback for older Python versions
        try:
            from importlib_metadata import version
            return version("pydantic-tfl-api")
        except ImportError:
            logger.debug("importlib_metadata not available, falling back to pyproject.toml")
    except Exception as e:
        error_msg = str(e).lower()
        if any(keyword in error_msg for keyword in ["not found", "no package metadata", "no such distribution"]):
            logger.debug("Package 'pydantic-tfl-api' not installed or metadata missing, falling back to pyproject.toml")
        else:
            logger.warning("Unexpected error retrieving version from metadata: %s", e)

    # Development fallback: read from pyproject.toml if available
    try:
        import tomllib
        from pathlib import Path
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        return pyproject_data["project"]["version"]
    except FileNotFoundError:
        logger.debug("pyproject.toml not found, using fallback version")
    except Exception as e:
        logger.warning("Error reading version from pyproject.toml: %s", e)

    # Final fallback
    return "0.0.0"

__version__ = _get_version()
__all__ = [
    'AccidentStatsClient',
    'AirQualityClient',
    'BikePointClient',
    'CrowdingClient',
    'JourneyClient',
    'LiftDisruptionsClient',
    'LineClient',
    'ModeClient',
    'OccupancyClient',
    'PlaceClient',
    'RoadClient',
    'SearchClient',
    'StopPointClient',
    'VehicleClient',
    'models'
]
