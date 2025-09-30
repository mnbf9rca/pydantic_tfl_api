from pydantic import BaseModel, ConfigDict, Field

from .DbGeography import DbGeography
from .RoadDisruptionImpactArea import RoadDisruptionImpactArea
from .RoadDisruptionLine import RoadDisruptionLine
from .RoadDisruptionSchedule import RoadDisruptionSchedule
from .RoadProject import RoadProject
from .Street import Street


class RoadDisruption(BaseModel):
    id: str | None = Field(None)
    url: str | None = Field(None)
    point: str | None = Field(None)
    severity: str | None = Field(None)
    ordinal: int | None = Field(None)
    category: str | None = Field(None)
    subCategory: str | None = Field(None)
    comments: str | None = Field(None)
    currentUpdate: str | None = Field(None)
    currentUpdateDateTime: str | None = Field(None)
    corridorIds: list[str] | None = Field(None)
    startDateTime: str | None = Field(None)
    endDateTime: str | None = Field(None)
    lastModifiedTime: str | None = Field(None)
    levelOfInterest: str | None = Field(None)
    location: str | None = Field(None)
    status: str | None = Field(None)
    geography: DbGeography | None = Field(None)
    geometry: DbGeography | None = Field(None)
    streets: list[Street] | None = Field(None)
    isProvisional: bool | None = Field(None)
    hasClosures: bool | None = Field(None)
    linkText: str | None = Field(None)
    linkUrl: str | None = Field(None)
    roadProject: RoadProject | None = Field(None)
    publishStartDate: str | None = Field(None)
    publishEndDate: str | None = Field(None)
    timeFrame: str | None = Field(None)
    roadDisruptionLines: list[RoadDisruptionLine] | None = Field(None)
    roadDisruptionImpactAreas: list[RoadDisruptionImpactArea] | None = Field(None)
    recurringSchedules: list[RoadDisruptionSchedule] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
