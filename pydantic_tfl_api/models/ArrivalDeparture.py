from .DepartureStatusEnum import DepartureStatusEnum
from .PredictionTiming import PredictionTiming
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ArrivalDeparture(BaseModel):
    platformName: str | None = Field(None)
    destinationNaptanId: str | None = Field(None)
    destinationName: str | None = Field(None)
    naptanId: str | None = Field(None)
    stationName: str | None = Field(None)
    estimatedTimeOfArrival: str | None = Field(None)
    scheduledTimeOfArrival: str | None = Field(None)
    estimatedTimeOfDeparture: str | None = Field(None)
    scheduledTimeOfDeparture: str | None = Field(None)
    minutesAndSecondsToArrival: str | None = Field(None)
    minutesAndSecondsToDeparture: str | None = Field(None)
    cause: str | None = Field(None)
    departureStatus: DepartureStatusEnum | None = Field(None)
    timing: Optional[PredictionTiming] = Field(None)

    model_config = ConfigDict(from_attributes=True)
