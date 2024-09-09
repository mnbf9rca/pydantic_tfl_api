from pydantic import RootModel
from typing import List
from .StopPoint import StopPoint


class StopPointArray(RootModel[List[StopPoint]]):
    class Config:
        from_attributes = True

