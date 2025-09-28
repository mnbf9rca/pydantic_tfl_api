from pydantic import RootModel, ConfigDict
from typing import List
from .PlaceCategory import PlaceCategory


class StopPointCategoryArray(RootModel[List[PlaceCategory]]):

    model_config = ConfigDict(from_attributes=True)
