from pydantic import BaseModel, ConfigDict, Field

from .DbGeography import DbGeography


class RoadDisruptionImpactArea(BaseModel):
    id: int | None = Field(None)
    roadDisruptionId: str | None = Field(None)
    polygon: DbGeography | None = Field(None)
    startDate: str | None = Field(None)
    endDate: str | None = Field(None)
    startTime: str | None = Field(None)
    endTime: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
