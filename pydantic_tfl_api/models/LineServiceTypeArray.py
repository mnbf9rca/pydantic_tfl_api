from pydantic import ConfigDict, RootModel

from .LineServiceType import LineServiceType


class LineServiceTypeArray(RootModel[list[LineServiceType]]):

    model_config = ConfigDict(from_attributes=True)
