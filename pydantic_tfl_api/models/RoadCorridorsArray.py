from pydantic import RootModel
from typing import List
from .RoadCorridor import RoadCorridor


class RoadCorridorsArray(RootModel[List[RoadCorridor]]):

    model_config = {'from_attributes': True}
