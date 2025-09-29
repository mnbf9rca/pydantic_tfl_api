from pydantic import RootModel, ConfigDict
from typing import List
from .RoadDisruption import RoadDisruption


class RoadDisruptionsArray(RootModel[list[RoadDisruption]]):

    model_config = ConfigDict(from_attributes=True)
