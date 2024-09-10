from pydantic import RootModel
from typing import List
from .Line import Line


class LineArray(RootModel[List[Line]]):

    model_config = {'from_attributes': True}
