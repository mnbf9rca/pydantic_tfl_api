from pydantic import ConfigDict, RootModel

from .AccidentDetail import AccidentDetail


class AccidentDetailArray(RootModel[list[AccidentDetail]]):

    model_config = ConfigDict(from_attributes=True)
