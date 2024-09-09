from pydantic import BaseModel, Field
from .StopPoint import StopPoint
from pydantic import BaseModel, Field
from typing import List, Optional


class StopPointsResponse(BaseModel):
    centrePoint: Optional[List[float]] = Field(None, alias='centrePoint')
    stopPoints: Optional[List[StopPoint]] = Field(None, alias='stopPoints')
    pageSize: Optional[int] = Field(None, alias='pageSize')
    total: Optional[int] = Field(None, alias='total')
    page: Optional[int] = Field(None, alias='page')

    class Config:
        from_attributes = True
