from pydantic import BaseModel, ConfigDict, Field

from .DepartureStatusEnum import DepartureStatusEnum
from .PredictionTiming import PredictionTiming


class ArrivalDeparture(BaseModel):
    """DTO to capture the prediction details"""

    platformName: str | None = Field(None, description="Platform name (for bus, this is the stop letter)")
    destinationNaptanId: str | None = Field(None, description="Naptan Identifier for the prediction's destination")
    destinationName: str | None = Field(None, description="Name of the destination")
    naptanId: str | None = Field(None, description="Identifier for the prediction")
    stationName: str | None = Field(None, description="Station name")
    estimatedTimeOfArrival: str | None = Field(None, description="Estimated time of arrival")
    scheduledTimeOfArrival: str | None = Field(None, description="Estimated time of arrival")
    estimatedTimeOfDeparture: str | None = Field(None, description="Estimated time of arrival")
    scheduledTimeOfDeparture: str | None = Field(None, description="Estimated time of arrival")
    minutesAndSecondsToArrival: str | None = Field(None, description="Estimated time of arrival")
    minutesAndSecondsToDeparture: str | None = Field(None, description="Estimated time of arrival")
    cause: str | None = Field(None, description="Reason for cancellation or delay")
    departureStatus: DepartureStatusEnum | None = Field(None, description="Status of departure")
    timing: PredictionTiming | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
