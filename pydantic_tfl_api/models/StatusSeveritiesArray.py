from pydantic import RootModel
from typing import List
from .StatusSeverity import StatusSeverity


class StatusSeveritiesArray(RootModel[List[StatusSeverity]]):

    model_config = {'from_attributes': True}
