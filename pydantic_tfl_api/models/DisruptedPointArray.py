from pydantic import RootModel
from typing import List
from .DisruptedPoint import DisruptedPoint


class DisruptedPointArray(RootModel[List[DisruptedPoint]]):

    model_config = {'from_attributes': True}
