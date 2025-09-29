from pydantic import BaseModel, ConfigDict, Field

from .CategoryEnum import CategoryEnum
from .RouteSection import RouteSection
from .StopPoint import StopPoint


class Disruption(BaseModel):
    category: CategoryEnum | None = Field(None)
    type: str | None = Field(None)
    categoryDescription: str | None = Field(None)
    description: str | None = Field(None)
    summary: str | None = Field(None)
    additionalInfo: str | None = Field(None)
    created: str | None = Field(None)
    lastUpdate: str | None = Field(None)
    affectedRoutes: list[RouteSection] | None = Field(None)
    affectedStops: list[StopPoint] | None = Field(None)
    closureText: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
