from pydantic import RootModel, ConfigDict
from typing import List
from .ArrivalDeparture import ArrivalDeparture


class ArrivalDepartureArray(RootModel[list[ArrivalDeparture]]):

    model_config = ConfigDict(from_attributes=True)
