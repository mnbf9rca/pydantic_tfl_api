from pydantic import RootModel, ConfigDict
from typing import List
from .Place import Place


class PlaceArray(RootModel[List[Place]]):

    model_config = ConfigDict(from_attributes=True)
