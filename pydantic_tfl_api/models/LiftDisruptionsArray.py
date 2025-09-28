from pydantic import RootModel, ConfigDict
from typing import List
from .LiftDisruption import LiftDisruption


class LiftDisruptionsArray(RootModel[List[LiftDisruption]]):

    model_config = ConfigDict(from_attributes=True)
