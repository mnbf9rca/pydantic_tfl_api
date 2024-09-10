from pydantic import RootModel
from typing import List
from .PlaceCategory import PlaceCategory


class StopPointCategoryArray(RootModel[List[PlaceCategory]]):

    model_config = {'from_attributes': True}
