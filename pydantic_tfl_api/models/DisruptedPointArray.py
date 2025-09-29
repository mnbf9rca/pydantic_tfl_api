from .DisruptedPoint import DisruptedPoint
from pydantic import RootModel, ConfigDict


class DisruptedPointArray(RootModel[list[DisruptedPoint]]):

    model_config = ConfigDict(from_attributes=True)
