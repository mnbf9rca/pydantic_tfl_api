from pydantic import RootModel
from typing import List
from .DisruptedPoint import DisruptedPoint


class DisruptedPointArray(RootModel[List[DisruptedPoint]]):
    class Config:
        from_attributes = True

