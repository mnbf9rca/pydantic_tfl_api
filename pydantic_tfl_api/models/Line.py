from pydantic import BaseModel, ConfigDict, Field

from .Crowding import Crowding
from .Disruption import Disruption
from .LineServiceTypeInfo import LineServiceTypeInfo
from .LineStatus import LineStatus
from .MatchedRoute import MatchedRoute


class Line(BaseModel):
    id: str | None = Field(None)
    name: str | None = Field(None)
    modeName: str | None = Field(None)
    disruptions: list[Disruption] | None = Field(None)
    created: str | None = Field(None)
    modified: str | None = Field(None)
    lineStatuses: list[LineStatus] | None = Field(None)
    routeSections: list[MatchedRoute] | None = Field(None)
    serviceTypes: list[LineServiceTypeInfo] | None = Field(None)
    crowding: Crowding | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
