from .DbGeography import DbGeography
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class RoadDisruptionImpactArea(BaseModel):
    id: int | None = Field(None)
    roadDisruptionId: str | None = Field(None)
    polygon: Optional[DbGeography] = Field(None)
    startDate: str | None = Field(None)
    endDate: str | None = Field(None)
    startTime: str | None = Field(None)
    endTime: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
