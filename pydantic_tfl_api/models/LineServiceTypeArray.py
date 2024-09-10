from pydantic import RootModel
from typing import List
from .LineServiceType import LineServiceType


class LineServiceTypeArray(RootModel[List[LineServiceType]]):

    model_config = {'from_attributes': True}
