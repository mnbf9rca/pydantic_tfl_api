from .DepartureStatusEnum import DepartureStatusEnum
from .PredictionTiming import PredictionTiming
from pydantic import BaseModel, Field
from typing import Optional


class ArrivalDeparture(BaseModel):
    platformName: Optional[str] = Field(None, alias='platformName')
    destinationNaptanId: Optional[str] = Field(None, alias='destinationNaptanId')
    destinationName: Optional[str] = Field(None, alias='destinationName')
    naptanId: Optional[str] = Field(None, alias='naptanId')
    stationName: Optional[str] = Field(None, alias='stationName')
    estimatedTimeOfArrival: Optional[str] = Field(None, alias='estimatedTimeOfArrival')
    scheduledTimeOfArrival: Optional[str] = Field(None, alias='scheduledTimeOfArrival')
    estimatedTimeOfDeparture: Optional[str] = Field(None, alias='estimatedTimeOfDeparture')
    scheduledTimeOfDeparture: Optional[str] = Field(None, alias='scheduledTimeOfDeparture')
    minutesAndSecondsToArrival: Optional[str] = Field(None, alias='minutesAndSecondsToArrival')
    minutesAndSecondsToDeparture: Optional[str] = Field(None, alias='minutesAndSecondsToDeparture')
    cause: Optional[str] = Field(None, alias='cause')
    departureStatus: Optional[DepartureStatusEnum] = Field(None, alias='departureStatus')
    timing: Optional[PredictionTiming] = Field(None, alias='timing')

    model_config = {'from_attributes': True}
