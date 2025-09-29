from .ArrivalDeparture import ArrivalDeparture
from pydantic import RootModel, ConfigDict


class ArrivalDepartureArray(RootModel[list[ArrivalDeparture]]):

    model_config = ConfigDict(from_attributes=True)
