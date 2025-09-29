from pydantic import RootModel, ConfigDict
from .Disruption import Disruption


class DisruptionArray(RootModel[list[Disruption]]):

    model_config = ConfigDict(from_attributes=True)
