from pydantic import RootModel
from typing import List
from .AccidentDetail import AccidentDetail


class AccidentDetailArray(RootModel[List[AccidentDetail]]):

    model_config = {'from_attributes': True}
