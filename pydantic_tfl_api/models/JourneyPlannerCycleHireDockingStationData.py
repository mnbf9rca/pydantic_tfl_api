from pydantic import BaseModel, ConfigDict, Field


class JourneyPlannerCycleHireDockingStationData(BaseModel):
    originNumberOfBikes: int | None = Field(None)
    destinationNumberOfBikes: int | None = Field(None)
    originNumberOfEmptySlots: int | None = Field(None)
    destinationNumberOfEmptySlots: int | None = Field(None)
    originId: str | None = Field(None)
    destinationId: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
