from .MatchedStop import MatchedStop
from .OrderedRoute import OrderedRoute
from .StopPointSequence import StopPointSequence
from pydantic import BaseModel, Field
from typing import List, Match, Optional, Sequence


class RouteSequence(BaseModel):
    lineId: Optional[str] = Field(None, alias='lineId')
    lineName: Optional[str] = Field(None, alias='lineName')
    direction: Optional[str] = Field(None, alias='direction')
    isOutboundOnly: Optional[bool] = Field(None, alias='isOutboundOnly')
    mode: Optional[str] = Field(None, alias='mode')
    lineStrings: Optional[list[str]] = Field(None, alias='lineStrings')
    stations: Optional[list[MatchedStop]] = Field(None, alias='stations')
    stopPointSequences: Optional[list[StopPointSequence]] = Field(None, alias='stopPointSequences')
    orderedLineRoutes: Optional[list[OrderedRoute]] = Field(None, alias='orderedLineRoutes')

    model_config = {'from_attributes': True}
