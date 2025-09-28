from .LineRouteSection import LineRouteSection
from .MatchedRouteSections import MatchedRouteSections
from .MatchedStop import MatchedStop
from pydantic import BaseModel, Field, ConfigDict
from typing import Match


class RouteSearchMatch(BaseModel):
    lineId: str | None = Field(None)
    mode: str | None = Field(None)
    lineName: str | None = Field(None)
    lineRouteSection: list[LineRouteSection] | None = Field(None)
    matchedRouteSections: list[MatchedRouteSections] | None = Field(None)
    matchedStops: list[MatchedStop] | None = Field(None)
    id: str | None = Field(None)
    url: str | None = Field(None)
    name: str | None = Field(None)
    lat: float | None = Field(None)
    lon: float | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
