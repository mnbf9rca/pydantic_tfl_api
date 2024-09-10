from pydantic import RootModel
from typing import List
from .Mode import Mode


class ModeArray(RootModel[List[Mode]]):

    model_config = {'from_attributes': True}
