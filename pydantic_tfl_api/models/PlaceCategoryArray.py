from pydantic import RootModel
from typing import List
from .PlaceCategory import PlaceCategory


class PlaceCategoryArray(RootModel[List[PlaceCategory]]):

    model_config = {'from_attributes': True}
