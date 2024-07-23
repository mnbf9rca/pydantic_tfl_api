from pydantic import BaseModel, Field
from typing import Optional

from .identifier import Identifier

class MatchedStop(BaseModel):
    station_id: Optional[str] = Field(None, alias='stationId')
    ics_id: str = Field(alias='icsId')
    top_most_parent_id: Optional[str] = Field(None, alias='topMostParentId')
    modes: list[str]
    stop_type: str = Field(alias='stopType')
    zone: Optional[str] = Field(None, alias='zone')
    lines: Optional[list[Identifier]] = Field([], alias='lines')
    status: bool = Field(alias='status')
    id: str = Field(alias='id')
    name: str = Field(alias='name')
    lat: float = Field(alias='lat')
    lon: float = Field(alias='lon')