from pydantic import RootModel
from typing import List
from .Disruption import Disruption


class DisruptionArray(RootModel[List[Disruption]]):

    model_config = {'from_attributes': True}
