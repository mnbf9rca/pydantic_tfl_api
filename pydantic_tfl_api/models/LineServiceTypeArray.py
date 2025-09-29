from .LineServiceType import LineServiceType
from pydantic import RootModel, ConfigDict


class LineServiceTypeArray(RootModel[list[LineServiceType]]):

    model_config = ConfigDict(from_attributes=True)
