from pydantic import RootModel
from typing import List
from .LiftDisruption import LiftDisruption


class LiftDisruptionsArray(RootModel[List[LiftDisruption]]):
    class Config:
        from_attributes = True

