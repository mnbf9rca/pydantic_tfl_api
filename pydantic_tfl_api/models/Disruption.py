from pydantic import BaseModel, ConfigDict, Field

from .CategoryEnum import CategoryEnum
from .RouteSection import RouteSection
from .StopPoint import StopPoint


class Disruption(BaseModel):
    """Represents a disruption to a route within the transport network."""

    category: CategoryEnum | None = Field(None, description="Gets or sets the category of this dispruption.")
    type: str | None = Field(None, description="Gets or sets the disruption type of this dispruption.")
    categoryDescription: str | None = Field(None, description="Gets or sets the description of the category.")
    description: str | None = Field(None, description="Gets or sets the description of this disruption.")
    summary: str | None = Field(None, description="Gets or sets the summary of this disruption.")
    additionalInfo: str | None = Field(None, description="Gets or sets the additionaInfo of this disruption.")
    created: str | None = Field(None, description="Gets or sets the date/time when this disruption was created.")
    lastUpdate: str | None = Field(None, description="Gets or sets the date/time when this disruption was last updated.")
    affectedRoutes: list[RouteSection] | None = Field(None, description="Gets or sets the routes affected by this disruption")
    affectedStops: list[StopPoint] | None = Field(None, description="Gets or sets the stops affected by this disruption")
    closureText: str | None = Field(None, description="Text describing the closure type")

    model_config = ConfigDict(from_attributes=True)
