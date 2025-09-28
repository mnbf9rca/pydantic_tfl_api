from pydantic import RootModel, ConfigDict
from typing import List
from .Line import Line


class LineArray(RootModel[List[Line]]):

    model_config = ConfigDict(from_attributes=True)
