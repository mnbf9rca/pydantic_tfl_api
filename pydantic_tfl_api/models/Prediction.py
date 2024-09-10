from .PredictionTiming import PredictionTiming
from pydantic import BaseModel, Field
from typing import Optional


class Prediction(BaseModel):
    id: Optional[str] = Field(None, alias='id')
    operationType: Optional[int] = Field(None, alias='operationType')
    vehicleId: Optional[str] = Field(None, alias='vehicleId')
    naptanId: Optional[str] = Field(None, alias='naptanId')
    stationName: Optional[str] = Field(None, alias='stationName')
    lineId: Optional[str] = Field(None, alias='lineId')
    lineName: Optional[str] = Field(None, alias='lineName')
    platformName: Optional[str] = Field(None, alias='platformName')
    direction: Optional[str] = Field(None, alias='direction')
    bearing: Optional[str] = Field(None, alias='bearing')
    destinationNaptanId: Optional[str] = Field(None, alias='destinationNaptanId')
    destinationName: Optional[str] = Field(None, alias='destinationName')
    timestamp: Optional[str] = Field(None, alias='timestamp')
    timeToStation: Optional[int] = Field(None, alias='timeToStation')
    currentLocation: Optional[str] = Field(None, alias='currentLocation')
    towards: Optional[str] = Field(None, alias='towards')
    expectedArrival: Optional[str] = Field(None, alias='expectedArrival')
    timeToLive: Optional[str] = Field(None, alias='timeToLive')
    modeName: Optional[str] = Field(None, alias='modeName')
    timing: Optional[PredictionTiming] = Field(None, alias='timing')

    model_config = {'from_attributes': True}
