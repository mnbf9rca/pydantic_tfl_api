from pydantic import RootModel, ConfigDict
from typing import List
from .DisruptedPoint import DisruptedPoint


class DisruptedPointArray(RootModel[List[DisruptedPoint]]):

    model_config = ConfigDict(from_attributes=True)
