from pydantic import RootModel
from typing import List
from .ArrivalDeparture import ArrivalDeparture


class ArrivalDepartureArray(RootModel[List[ArrivalDeparture]]):

    model_config = {'from_attributes': True}
