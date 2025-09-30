from pydantic import BaseModel, ConfigDict, Field

from .Journey import Journey
from .JourneyPlannerCycleHireDockingStationData import JourneyPlannerCycleHireDockingStationData
from .JourneyVector import JourneyVector
from .Line import Line
from .SearchCriteria import SearchCriteria


class ItineraryResult(BaseModel):
    """A DTO representing a list of possible journeys."""

    journeys: list[Journey] | None = Field(None)
    lines: list[Line] | None = Field(None)
    cycleHireDockingStationData: JourneyPlannerCycleHireDockingStationData | None = Field(None)
    stopMessages: list[str] | None = Field(None)
    recommendedMaxAgeMinutes: int | None = Field(None)
    searchCriteria: SearchCriteria | None = Field(None)
    journeyVector: JourneyVector | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
