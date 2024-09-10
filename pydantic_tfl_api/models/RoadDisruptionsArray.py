from pydantic import RootModel
from typing import List
from .RoadDisruption import RoadDisruption


class RoadDisruptionsArray(RootModel[List[RoadDisruption]]):

    model_config = {'from_attributes': True}
