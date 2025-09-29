from pydantic import ConfigDict, RootModel

from .StopPoint import StopPoint


class StopPointArray(RootModel[list[StopPoint]]):

    model_config = ConfigDict(from_attributes=True)
