from pydantic import RootModel
from typing import List
from .AccidentDetail import AccidentDetail


class AccidentDetailArray(RootModel[List[AccidentDetail]]):
    class Config:
        from_attributes = True

