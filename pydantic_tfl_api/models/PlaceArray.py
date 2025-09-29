from pydantic import RootModel, ConfigDict
from typing import List
from .Place import Place


class PlaceArray(RootModel[list[Place]]):

    model_config = ConfigDict(from_attributes=True)
