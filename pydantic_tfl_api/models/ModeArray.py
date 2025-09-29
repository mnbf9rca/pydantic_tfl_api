from pydantic import RootModel, ConfigDict
from typing import List
from .Mode import Mode


class ModeArray(RootModel[list[Mode]]):

    model_config = ConfigDict(from_attributes=True)
