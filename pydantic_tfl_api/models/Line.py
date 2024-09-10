from .Crowding import Crowding
from .Disruption import Disruption
from .LineServiceTypeInfo import LineServiceTypeInfo
from .LineStatus import LineStatus
from .MatchedRoute import MatchedRoute
from pydantic import BaseModel, Field
from typing import List, Match, Optional, Type


class Line(BaseModel):
    id: Optional[str] = Field(None, alias='id')
    name: Optional[str] = Field(None, alias='name')
    modeName: Optional[str] = Field(None, alias='modeName')
    disruptions: Optional[list[Disruption]] = Field(None, alias='disruptions')
    created: Optional[str] = Field(None, alias='created')
    modified: Optional[str] = Field(None, alias='modified')
    lineStatuses: Optional[list[LineStatus]] = Field(None, alias='lineStatuses')
    routeSections: Optional[list[MatchedRoute]] = Field(None, alias='routeSections')
    serviceTypes: Optional[list[LineServiceTypeInfo]] = Field(None, alias='serviceTypes')
    crowding: Optional[Crowding] = Field(None, alias='crowding')

    model_config = {'from_attributes': True}
