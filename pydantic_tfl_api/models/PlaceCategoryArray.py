from pydantic import ConfigDict, RootModel

from .PlaceCategory import PlaceCategory


class PlaceCategoryArray(RootModel[list[PlaceCategory]]):

    model_config = ConfigDict(from_attributes=True)
