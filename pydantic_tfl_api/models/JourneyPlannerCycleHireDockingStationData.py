from pydantic import BaseModel, Field
from typing import Optional


class JourneyPlannerCycleHireDockingStationData(BaseModel):
    originNumberOfBikes: Optional[int] = Field(None, alias='originNumberOfBikes')
    destinationNumberOfBikes: Optional[int] = Field(None, alias='destinationNumberOfBikes')
    originNumberOfEmptySlots: Optional[int] = Field(None, alias='originNumberOfEmptySlots')
    destinationNumberOfEmptySlots: Optional[int] = Field(None, alias='destinationNumberOfEmptySlots')
    originId: Optional[str] = Field(None, alias='originId')
    destinationId: Optional[str] = Field(None, alias='destinationId')

    model_config = {'from_attributes': True}
