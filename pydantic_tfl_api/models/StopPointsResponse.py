from .StopPoint import StopPoint
from pydantic import BaseModel, Field
from typing import List, Optional


class StopPointsResponse(BaseModel):
    centrePoint: Optional[list[float]] = Field(None, alias='centrePoint')
    stopPoints: Optional[list[StopPoint]] = Field(None, alias='stopPoints')
    pageSize: Optional[int] = Field(None, alias='pageSize')
    total: Optional[int] = Field(None, alias='total')
    page: Optional[int] = Field(None, alias='page')

    class Config:
        from_attributes = True
