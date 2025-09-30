from pydantic import ConfigDict, RootModel

from .Line import Line


class LineArray(RootModel[list[Line]]):

    model_config = ConfigDict(from_attributes=True)
