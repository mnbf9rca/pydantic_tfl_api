from pydantic import RootModel
from typing import List
from .Disruption import Disruption


class DisruptionArray(RootModel[List[Disruption]]):
    class Config:
        from_attributes = True

