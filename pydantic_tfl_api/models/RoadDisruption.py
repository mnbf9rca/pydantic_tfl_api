from pydantic import BaseModel, ConfigDict, Field

from .DbGeography import DbGeography
from .RoadDisruptionImpactArea import RoadDisruptionImpactArea
from .RoadDisruptionLine import RoadDisruptionLine
from .RoadDisruptionSchedule import RoadDisruptionSchedule
from .RoadProject import RoadProject
from .Street import Street


class RoadDisruption(BaseModel):
    id: str | None = Field(None, description="Unique identifier for the road disruption")
    url: str | None = Field(None, description="URL to retrieve this road disruption")
    point: str | None = Field(None, description="Latitude and longitude (WGS84) of the centroid of the disruption, stored in a geoJSON-formatted string.")
    severity: str | None = Field(None, description="A description of the severity of the disruption.")
    ordinal: int | None = Field(None, description="An ordinal of the disruption based on severity, level of interest and corridor.")
    category: str | None = Field(None, description="Describes the nature of disruption e.g. Traffic Incidents, Works")
    subCategory: str | None = Field(None, description="Describes the sub-category of disruption e.g. Collapsed Manhole, Abnormal Load")
    comments: str | None = Field(None, description="Full text of comments describing the disruption, including details of any road closures and diversions, where appropriate.")
    currentUpdate: str | None = Field(None, description="Text of the most recent update from the LSTCC on the state of the disruption, including the current traffic impact and any advice to road users.")
    currentUpdateDateTime: str | None = Field(None, description="The time when the last CurrentUpdate description was recorded, or null if no CurrentUpdate has been applied.")
    corridorIds: list[str] | None = Field(None, description="The Ids of affected corridors, if any.")
    startDateTime: str | None = Field(None, description="The date and time which the disruption started. For a planned disruption (i.e. planned road works) this date will be in the future. For unplanned disruptions, this will default to the date on which the disruption was first recorded, but may be adjusted by the operator.")
    endDateTime: str | None = Field(None, description="The date and time on which the disruption ended. For planned disruptions, this date will have a valid value. For unplanned disruptions in progress, this field will be omitted.")
    lastModifiedTime: str | None = Field(None, description="The date and time on which the disruption was last modified in the system. This information can reliably be used by a developer to quickly compare two instances of the same disruption to determine if it has been changed.")
    levelOfInterest: str | None = Field(None, description="This describes the level of potential impact on traffic operations of the disruption. High = e.g. a one-off disruption on a major or high profile route which will require a high level of operational attention Medium = This is the default value Low = e.g. a frequently occurring disruption which is well known")
    location: str | None = Field(None, description="Main road name / number (borough) or preset area name where the disruption is located. This might be useful for a map popup where space is limited.")
    status: str | None = Field(None, description="This describes the status of the disruption. Active = currently in progress Active Long Term = currently in progress and long term Scheduled = scheduled to start within the next 180 days Recurring Works = planned maintenance works that follow a regular routine or pattern and whose next occurrence is to start within the next 180 days. Recently Cleared = recently cleared in the last 24 hours Note that the status of Scheduled or Recurring Works disruptions will change to Active when they start, and will change status again when they end.")
    geography: DbGeography | None = Field(None)
    geometry: DbGeography | None = Field(None)
    streets: list[Street] | None = Field(None, description="A collection of zero or more streets affected by the disruption.")
    isProvisional: bool | None = Field(None, description="True if the disruption is planned on a future date that is open to change")
    hasClosures: bool | None = Field(None, description="True if any of the affected Streets have a \"Full Closure\" status, false otherwise. A RoadDisruption that has HasClosures is considered a Severe or Serious disruption for severity filtering purposes.")
    linkText: str | None = Field(None, description="The text of any associated link")
    linkUrl: str | None = Field(None, description="The url of any associated link")
    roadProject: RoadProject | None = Field(None)
    publishStartDate: str | None = Field(None, description="TDM Additional properties")
    publishEndDate: str | None = Field(None)
    timeFrame: str | None = Field(None)
    roadDisruptionLines: list[RoadDisruptionLine] | None = Field(None)
    roadDisruptionImpactAreas: list[RoadDisruptionImpactArea] | None = Field(None)
    recurringSchedules: list[RoadDisruptionSchedule] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
