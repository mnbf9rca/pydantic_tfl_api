from pydantic import RootModel
from typing import List
from .Line import Line


class LineArray(RootModel[List[Line]]):
    class Config:
        from_attributes = True

