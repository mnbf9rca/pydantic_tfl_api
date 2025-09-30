from pydantic import ConfigDict, RootModel

from .LiftDisruption import LiftDisruption


class LiftDisruptionsArray(RootModel[list[LiftDisruption]]):

    model_config = ConfigDict(from_attributes=True)
