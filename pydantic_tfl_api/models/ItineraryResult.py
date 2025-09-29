from .Journey import Journey
from .JourneyPlannerCycleHireDockingStationData import JourneyPlannerCycleHireDockingStationData
from .JourneyVector import JourneyVector
from .Line import Line
from .SearchCriteria import SearchCriteria
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ItineraryResult(BaseModel):
    journeys: list[Journey] | None = Field(None)
    lines: list[Line] | None = Field(None)
    cycleHireDockingStationData: Optional[JourneyPlannerCycleHireDockingStationData] = Field(None)
    stopMessages: list[str] | None = Field(None)
    recommendedMaxAgeMinutes: int | None = Field(None)
    searchCriteria: Optional[SearchCriteria] = Field(None)
    journeyVector: Optional[JourneyVector] = Field(None)

    model_config = ConfigDict(from_attributes=True)
