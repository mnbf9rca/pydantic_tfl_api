from .DbGeography import DbGeography
from .RoadDisruptionImpactArea import RoadDisruptionImpactArea
from .RoadDisruptionLine import RoadDisruptionLine
from .RoadDisruptionSchedule import RoadDisruptionSchedule
from .RoadProject import RoadProject
from .Street import Street
from pydantic import BaseModel, Field
from typing import List, Optional


class RoadDisruption(BaseModel):
    id: Optional[str] = Field(None, alias='id')
    url: Optional[str] = Field(None, alias='url')
    point: Optional[str] = Field(None, alias='point')
    severity: Optional[str] = Field(None, alias='severity')
    ordinal: Optional[int] = Field(None, alias='ordinal')
    category: Optional[str] = Field(None, alias='category')
    subCategory: Optional[str] = Field(None, alias='subCategory')
    comments: Optional[str] = Field(None, alias='comments')
    currentUpdate: Optional[str] = Field(None, alias='currentUpdate')
    currentUpdateDateTime: Optional[str] = Field(None, alias='currentUpdateDateTime')
    corridorIds: Optional[list[str]] = Field(None, alias='corridorIds')
    startDateTime: Optional[str] = Field(None, alias='startDateTime')
    endDateTime: Optional[str] = Field(None, alias='endDateTime')
    lastModifiedTime: Optional[str] = Field(None, alias='lastModifiedTime')
    levelOfInterest: Optional[str] = Field(None, alias='levelOfInterest')
    location: Optional[str] = Field(None, alias='location')
    status: Optional[str] = Field(None, alias='status')
    geography: Optional[DbGeography] = Field(None, alias='geography')
    geometry: Optional[DbGeography] = Field(None, alias='geometry')
    streets: Optional[list[Street]] = Field(None, alias='streets')
    isProvisional: Optional[bool] = Field(None, alias='isProvisional')
    hasClosures: Optional[bool] = Field(None, alias='hasClosures')
    linkText: Optional[str] = Field(None, alias='linkText')
    linkUrl: Optional[str] = Field(None, alias='linkUrl')
    roadProject: Optional[RoadProject] = Field(None, alias='roadProject')
    publishStartDate: Optional[str] = Field(None, alias='publishStartDate')
    publishEndDate: Optional[str] = Field(None, alias='publishEndDate')
    timeFrame: Optional[str] = Field(None, alias='timeFrame')
    roadDisruptionLines: Optional[list[RoadDisruptionLine]] = Field(None, alias='roadDisruptionLines')
    roadDisruptionImpactAreas: Optional[list[RoadDisruptionImpactArea]] = Field(None, alias='roadDisruptionImpactAreas')
    recurringSchedules: Optional[list[RoadDisruptionSchedule]] = Field(None, alias='recurringSchedules')

    model_config = {'from_attributes': True}
