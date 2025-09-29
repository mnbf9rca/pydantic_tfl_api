from pydantic import RootModel, ConfigDict
from typing import List
from .StatusSeverity import StatusSeverity


class StatusSeveritiesArray(RootModel[list[StatusSeverity]]):

    model_config = ConfigDict(from_attributes=True)
