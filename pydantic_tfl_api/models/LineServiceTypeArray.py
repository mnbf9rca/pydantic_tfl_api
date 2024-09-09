from pydantic import RootModel
from typing import List
from .LineServiceType import LineServiceType


class LineServiceTypeArray(RootModel[List[LineServiceType]]):
    class Config:
        from_attributes = True

