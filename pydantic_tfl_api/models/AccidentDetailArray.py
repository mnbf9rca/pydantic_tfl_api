from pydantic import RootModel, ConfigDict
from typing import List
from .AccidentDetail import AccidentDetail


class AccidentDetailArray(RootModel[List[AccidentDetail]]):

    model_config = ConfigDict(from_attributes=True)
