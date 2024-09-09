from pydantic import RootModel
from typing import List
from .Place import Place


class PlaceArray(RootModel[List[Place]]):
    class Config:
        from_attributes = True

