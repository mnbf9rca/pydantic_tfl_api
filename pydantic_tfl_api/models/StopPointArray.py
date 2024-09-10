from pydantic import RootModel
from typing import List
from .StopPoint import StopPoint


class StopPointArray(RootModel[List[StopPoint]]):

    model_config = {'from_attributes': True}
