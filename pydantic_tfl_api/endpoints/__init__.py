from typing import Literal

from .LineClient import AsyncLineClient, LineClient
from .AirQualityClient import AsyncAirQualityClient, AirQualityClient
from .OccupancyClient import AsyncOccupancyClient, OccupancyClient
from .VehicleClient import AsyncVehicleClient, VehicleClient
from .CrowdingClient import AsyncCrowdingClient, CrowdingClient
from .BikePointClient import AsyncBikePointClient, BikePointClient
from .SearchClient import AsyncSearchClient, SearchClient
from .AccidentStatsClient import AsyncAccidentStatsClient, AccidentStatsClient
from .JourneyClient import AsyncJourneyClient, JourneyClient
from .RoadClient import AsyncRoadClient, RoadClient
from .PlaceClient import AsyncPlaceClient, PlaceClient
from .ModeClient import AsyncModeClient, ModeClient
from .StopPointClient import AsyncStopPointClient, StopPointClient
from .LiftDisruptionsClient import AsyncLiftDisruptionsClient, LiftDisruptionsClient

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

AsyncTfLEndpoint = Literal[
    "AsyncLineClient",
    "AsyncAirQualityClient",
    "AsyncOccupancyClient",
    "AsyncVehicleClient",
    "AsyncCrowdingClient",
    "AsyncBikePointClient",
    "AsyncSearchClient",
    "AsyncAccidentStatsClient",
    "AsyncJourneyClient",
    "AsyncRoadClient",
    "AsyncPlaceClient",
    "AsyncModeClient",
    "AsyncStopPointClient",
    "AsyncLiftDisruptionsClient",
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
    "AsyncLineClient",
    "AsyncAirQualityClient",
    "AsyncOccupancyClient",
    "AsyncVehicleClient",
    "AsyncCrowdingClient",
    "AsyncBikePointClient",
    "AsyncSearchClient",
    "AsyncAccidentStatsClient",
    "AsyncJourneyClient",
    "AsyncRoadClient",
    "AsyncPlaceClient",
    "AsyncModeClient",
    "AsyncStopPointClient",
    "AsyncLiftDisruptionsClient",
]
