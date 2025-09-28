from pydantic import RootModel, ConfigDict
from typing import List
from .RoadCorridor import RoadCorridor


class RoadCorridorsArray(RootModel[List[RoadCorridor]]):

    model_config = ConfigDict(from_attributes=True)
