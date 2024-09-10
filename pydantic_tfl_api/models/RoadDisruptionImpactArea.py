from .DbGeography import DbGeography
from pydantic import BaseModel, Field
from typing import Optional


class RoadDisruptionImpactArea(BaseModel):
    id: Optional[int] = Field(None, alias='id')
    roadDisruptionId: Optional[str] = Field(None, alias='roadDisruptionId')
    polygon: Optional[DbGeography] = Field(None, alias='polygon')
    startDate: Optional[str] = Field(None, alias='startDate')
    endDate: Optional[str] = Field(None, alias='endDate')
    startTime: Optional[str] = Field(None, alias='startTime')
    endTime: Optional[str] = Field(None, alias='endTime')

    model_config = {'from_attributes': True}
