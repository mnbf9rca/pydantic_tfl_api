from pydantic import BaseModel, Field
from .LineRouteSection import LineRouteSection
from .MatchedRouteSections import MatchedRouteSections
from .MatchedStop import MatchedStop
from pydantic import BaseModel, Field
from typing import List, Match, Optional


class RouteSearchMatch(BaseModel):
    lineId: Optional[str] = Field(None, alias='lineId')
    mode: Optional[str] = Field(None, alias='mode')
    lineName: Optional[str] = Field(None, alias='lineName')
    lineRouteSection: Optional[List[LineRouteSection]] = Field(None, alias='lineRouteSection')
    matchedRouteSections: Optional[List[MatchedRouteSections]] = Field(None, alias='matchedRouteSections')
    matchedStops: Optional[List[MatchedStop]] = Field(None, alias='matchedStops')
    id: Optional[str] = Field(None, alias='id')
    url: Optional[str] = Field(None, alias='url')
    name: Optional[str] = Field(None, alias='name')
    lat: Optional[float] = Field(None, alias='lat')
    lon: Optional[float] = Field(None, alias='lon')

    class Config:
        from_attributes = True
