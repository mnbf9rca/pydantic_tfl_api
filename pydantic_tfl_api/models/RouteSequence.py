from pydantic import BaseModel, ConfigDict, Field

from .MatchedStop import MatchedStop
from .OrderedRoute import OrderedRoute
from .StopPointSequence import StopPointSequence


class RouteSequence(BaseModel):
    lineId: str | None = Field(None)
    lineName: str | None = Field(None)
    direction: str | None = Field(None)
    isOutboundOnly: bool | None = Field(None)
    mode: str | None = Field(None)
    lineStrings: list[str] | None = Field(None)
    stations: list[MatchedStop] | None = Field(None)
    stopPointSequences: list[StopPointSequence] | None = Field(None)
    orderedLineRoutes: list[OrderedRoute] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
