from pydantic import RootModel, ConfigDict
from typing import List
from .Mode import Mode


class ModeArray(RootModel[List[Mode]]):

    model_config = ConfigDict(from_attributes=True)
