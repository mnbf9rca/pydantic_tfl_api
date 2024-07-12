from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from .prediction_timing import PredictionTiming

class Prediction(BaseModel):
    id: int = Field(alias='id')
    operation_type: int = Field(alias='operationType')
    vehicle_id: int = Field(alias='vehicleId')
    naptan_id: str = Field(alias='naptanId')
    station_name: str = Field(alias='stationName')
    line_id: str = Field(alias='lineId')
    line_name: str = Field(alias='lineName')
    platform_name: Optional[str] = Field(None, alias='platformName')
    direction: str = Field(alias='direction')
    bearing: str = Field(alias='bearing')
    destination_naptan_id: str = Field(alias='destinationNaptanId')
    destination_name: str = Field(alias='destinationName')
    timestamp: datetime = Field(alias='timestamp')
    time_to_station: int = Field(alias='timeToStation')
    current_location: str = Field(alias='currentLocation')
    towards: str = Field(alias='towards')
    expected_arrival: datetime = Field(alias='expectedArrival')
    time_to_live: datetime = Field(alias='timeToLive')
    mode_name: str = Field(alias='modeName')
    timing: PredictionTiming = Field(alias='timing')
    content_expires: Optional[datetime] = Field(None)

    model_config = {'populate_by_name': True}