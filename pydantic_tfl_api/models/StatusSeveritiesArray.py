from pydantic import ConfigDict, RootModel

from .StatusSeverity import StatusSeverity


class StatusSeveritiesArray(RootModel[list[StatusSeverity]]):

    model_config = ConfigDict(from_attributes=True)
