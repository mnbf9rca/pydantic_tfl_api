from pydantic import ConfigDict, RootModel

from .DisruptedPoint import DisruptedPoint


class DisruptedPointArray(RootModel[list[DisruptedPoint]]):

    model_config = ConfigDict(from_attributes=True)
