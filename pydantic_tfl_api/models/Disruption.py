from .CategoryEnum import CategoryEnum
from .RouteSection import RouteSection
from .StopPoint import StopPoint
from pydantic import BaseModel, Field
from typing import List, Optional


class Disruption(BaseModel):
    category: Optional[CategoryEnum] = Field(None, alias='category')
    type: Optional[str] = Field(None, alias='type')
    categoryDescription: Optional[str] = Field(None, alias='categoryDescription')
    description: Optional[str] = Field(None, alias='description')
    summary: Optional[str] = Field(None, alias='summary')
    additionalInfo: Optional[str] = Field(None, alias='additionalInfo')
    created: Optional[str] = Field(None, alias='created')
    lastUpdate: Optional[str] = Field(None, alias='lastUpdate')
    affectedRoutes: Optional[list[RouteSection]] = Field(None, alias='affectedRoutes')
    affectedStops: Optional[list[StopPoint]] = Field(None, alias='affectedStops')
    closureText: Optional[str] = Field(None, alias='closureText')

    model_config = {'from_attributes': True}
