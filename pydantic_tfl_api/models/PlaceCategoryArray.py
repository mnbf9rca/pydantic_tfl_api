from pydantic import RootModel
from typing import List
from .PlaceCategory import PlaceCategory


class PlaceCategoryArray(RootModel[List[PlaceCategory]]):
    class Config:
        from_attributes = True

