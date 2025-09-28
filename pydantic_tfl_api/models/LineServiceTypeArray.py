from pydantic import RootModel, ConfigDict
from typing import List
from .LineServiceType import LineServiceType


class LineServiceTypeArray(RootModel[List[LineServiceType]]):

    model_config = ConfigDict(from_attributes=True)
