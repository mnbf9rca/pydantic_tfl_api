from .Identifier import Identifier
from pydantic import BaseModel, Field
from typing import List, Optional


class MatchedStop(BaseModel):
    routeId: Optional[int] = Field(None, alias='routeId')
    parentId: Optional[str] = Field(None, alias='parentId')
    stationId: Optional[str] = Field(None, alias='stationId')
    icsId: Optional[str] = Field(None, alias='icsId')
    topMostParentId: Optional[str] = Field(None, alias='topMostParentId')
    direction: Optional[str] = Field(None, alias='direction')
    towards: Optional[str] = Field(None, alias='towards')
    modes: Optional[list[str]] = Field(None, alias='modes')
    stopType: Optional[str] = Field(None, alias='stopType')
    stopLetter: Optional[str] = Field(None, alias='stopLetter')
    zone: Optional[str] = Field(None, alias='zone')
    accessibilitySummary: Optional[str] = Field(None, alias='accessibilitySummary')
    hasDisruption: Optional[bool] = Field(None, alias='hasDisruption')
    lines: Optional[list[Identifier]] = Field(None, alias='lines')
    status: Optional[bool] = Field(None, alias='status')
    id: Optional[str] = Field(None, alias='id')
    url: Optional[str] = Field(None, alias='url')
    name: Optional[str] = Field(None, alias='name')
    lat: Optional[float] = Field(None, alias='lat')
    lon: Optional[float] = Field(None, alias='lon')

    model_config = {'from_attributes': True}
