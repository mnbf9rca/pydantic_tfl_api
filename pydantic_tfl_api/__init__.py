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
    try:
        # Python 3.8+ standard library approach
        from importlib.metadata import version
        return version("pydantic-tfl-api")
    except ImportError:
        # Fallback for older Python versions
        try:
            from importlib_metadata import version
            return version("pydantic-tfl-api")
        except ImportError:
            pass
    except Exception:
        # Package not installed or other error
        pass

    # Development fallback: read from pyproject.toml if available
    try:
        import tomllib
        from pathlib import Path
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        return pyproject_data["project"]["version"]
    except Exception:
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
