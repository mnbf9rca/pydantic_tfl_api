from pydantic import RootModel
from typing import List
from .ArrivalDeparture import ArrivalDeparture


class ArrivalDepartureArray(RootModel[List[ArrivalDeparture]]):
    class Config:
        from_attributes = True

