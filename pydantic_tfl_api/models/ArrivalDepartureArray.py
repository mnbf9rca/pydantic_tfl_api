from pydantic import ConfigDict, RootModel

from .ArrivalDeparture import ArrivalDeparture


class ArrivalDepartureArray(RootModel[list[ArrivalDeparture]]):

    model_config = ConfigDict(from_attributes=True)
