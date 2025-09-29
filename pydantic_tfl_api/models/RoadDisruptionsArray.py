from pydantic import ConfigDict, RootModel

from .RoadDisruption import RoadDisruption


class RoadDisruptionsArray(RootModel[list[RoadDisruption]]):

    model_config = ConfigDict(from_attributes=True)
