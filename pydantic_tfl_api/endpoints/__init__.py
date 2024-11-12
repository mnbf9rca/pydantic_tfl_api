from typing import Literal
from .AccidentStatsClient import AccidentStatsClient
from .AirQualityClient import AirQualityClient
from .BikePointClient import BikePointClient
from .CrowdingClient import CrowdingClient
from .JourneyClient import JourneyClient
from .LiftDisruptionsClient import LiftDisruptionsClient
from .LineClient import LineClient
from .ModeClient import ModeClient
from .OccupancyClient import OccupancyClient
from .PlaceClient import PlaceClient
from .RoadClient import RoadClient
from .SearchClient import SearchClient
from .StopPointClient import StopPointClient
from .VehicleClient import VehicleClient

TfLEndpoint = Literal[
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
    'VehicleClient'
]

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
    'VehicleClient'
]
