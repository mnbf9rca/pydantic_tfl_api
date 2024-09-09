from pydantic import RootModel
from typing import List
from .Mode import Mode


class ModeArray(RootModel[List[Mode]]):
    class Config:
        from_attributes = True

