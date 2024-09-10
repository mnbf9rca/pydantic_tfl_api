from pydantic import RootModel
from typing import List
from .LiftDisruption import LiftDisruption


class LiftDisruptionsArray(RootModel[List[LiftDisruption]]):

    model_config = {'from_attributes': True}
