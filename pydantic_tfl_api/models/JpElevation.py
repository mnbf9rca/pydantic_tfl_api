from pydantic import BaseModel, Field
from typing import Optional


class JpElevation(BaseModel):
    distance: Optional[int] = Field(None, alias='distance')
    startLat: Optional[float] = Field(None, alias='startLat')
    startLon: Optional[float] = Field(None, alias='startLon')
    endLat: Optional[float] = Field(None, alias='endLat')
    endLon: Optional[float] = Field(None, alias='endLon')
    heightFromPreviousPoint: Optional[int] = Field(None, alias='heightFromPreviousPoint')
    gradient: Optional[float] = Field(None, alias='gradient')

    model_config = {'from_attributes': True}
