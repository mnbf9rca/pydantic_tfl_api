from typing import Literal

from .LineClient import LineClient
from .AirQualityClient import AirQualityClient
from .OccupancyClient import OccupancyClient
from .VehicleClient import VehicleClient
from .CrowdingClient import CrowdingClient
from .BikePointClient import BikePointClient
from .SearchClient import SearchClient
from .AccidentStatsClient import AccidentStatsClient
from .JourneyClient import JourneyClient
from .RoadClient import RoadClient
from .PlaceClient import PlaceClient
from .ModeClient import ModeClient
from .StopPointClient import StopPointClient
from .LiftDisruptionsClient import LiftDisruptionsClient

TfLEndpoint = Literal[
    "LineClient",
    "AirQualityClient",
    "OccupancyClient",
    "VehicleClient",
    "CrowdingClient",
    "BikePointClient",
    "SearchClient",
    "AccidentStatsClient",
    "JourneyClient",
    "RoadClient",
    "PlaceClient",
    "ModeClient",
    "StopPointClient",
    "LiftDisruptionsClient",
]

__all__ = [
    "LineClient",
    "AirQualityClient",
    "OccupancyClient",
    "VehicleClient",
    "CrowdingClient",
    "BikePointClient",
    "SearchClient",
    "AccidentStatsClient",
    "JourneyClient",
    "RoadClient",
    "PlaceClient",
    "ModeClient",
    "StopPointClient",
    "LiftDisruptionsClient",
]
