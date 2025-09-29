from pydantic import RootModel, ConfigDict
from .StopPoint import StopPoint


class StopPointArray(RootModel[list[StopPoint]]):

    model_config = ConfigDict(from_attributes=True)
