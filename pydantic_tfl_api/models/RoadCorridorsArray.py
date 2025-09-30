from pydantic import ConfigDict, RootModel

from .RoadCorridor import RoadCorridor


class RoadCorridorsArray(RootModel[list[RoadCorridor]]):

    model_config = ConfigDict(from_attributes=True)
