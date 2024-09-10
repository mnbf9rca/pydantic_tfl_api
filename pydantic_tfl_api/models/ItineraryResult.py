from .Journey import Journey
from .JourneyPlannerCycleHireDockingStationData import JourneyPlannerCycleHireDockingStationData
from .JourneyVector import JourneyVector
from .Line import Line
from .SearchCriteria import SearchCriteria
from pydantic import BaseModel, Field
from typing import List, Optional


class ItineraryResult(BaseModel):
    journeys: Optional[list[Journey]] = Field(None, alias='journeys')
    lines: Optional[list[Line]] = Field(None, alias='lines')
    cycleHireDockingStationData: Optional[JourneyPlannerCycleHireDockingStationData] = Field(None, alias='cycleHireDockingStationData')
    stopMessages: Optional[list[str]] = Field(None, alias='stopMessages')
    recommendedMaxAgeMinutes: Optional[int] = Field(None, alias='recommendedMaxAgeMinutes')
    searchCriteria: Optional[SearchCriteria] = Field(None, alias='searchCriteria')
    journeyVector: Optional[JourneyVector] = Field(None, alias='journeyVector')

    model_config = {'from_attributes': True}
