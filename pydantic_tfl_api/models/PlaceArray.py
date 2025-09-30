from pydantic import ConfigDict, RootModel

from .Place import Place


class PlaceArray(RootModel[list[Place]]):

    model_config = ConfigDict(from_attributes=True)
