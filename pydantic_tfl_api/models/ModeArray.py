from pydantic import ConfigDict, RootModel

from .Mode import Mode


class ModeArray(RootModel[list[Mode]]):

    model_config = ConfigDict(from_attributes=True)
