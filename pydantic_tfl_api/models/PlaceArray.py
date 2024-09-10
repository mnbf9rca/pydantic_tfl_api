from pydantic import RootModel
from typing import List
from .Place import Place


class PlaceArray(RootModel[List[Place]]):

    model_config = {'from_attributes': True}
