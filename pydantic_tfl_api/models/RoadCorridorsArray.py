from pydantic import RootModel
from typing import List
from .RoadCorridor import RoadCorridor


class RoadCorridorsArray(RootModel[List[RoadCorridor]]):
    class Config:
        from_attributes = True

