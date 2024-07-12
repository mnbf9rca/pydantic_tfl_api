from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .matched_stop import MatchedStop
from .ordered_route import OrderedRoute

class RouteSequence(BaseModel):
    line_id: str = Field(alias='lineId')
    line_name: str = Field(alias='lineName')
    direction: str = Field(alias='direction')
    is_outbound_only: bool = Field(alias='isOutboundOnly')
    mode: str = Field(alias='mode')
    line_strings: list[str] = Field(alias='lineStrings')
    stations: list[MatchedStop] = Field(alias='stations')
    service_type: Optional[str] = Field(None, alias='serviceType')
    ordered_line_routes: list[OrderedRoute] = Field(alias='orderedLineRoutes')
    content_expires: Optional[datetime] = Field(None)
    
    model_config = {'populate_by_name': True}
