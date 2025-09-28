from pydantic import RootModel, ConfigDict
from typing import List
from .StatusSeverity import StatusSeverity


class StatusSeveritiesArray(RootModel[List[StatusSeverity]]):

    model_config = ConfigDict(from_attributes=True)
