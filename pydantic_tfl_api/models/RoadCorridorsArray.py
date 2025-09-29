from pydantic import RootModel, ConfigDict
from .RoadCorridor import RoadCorridor


class RoadCorridorsArray(RootModel[list[RoadCorridor]]):

    model_config = ConfigDict(from_attributes=True)
