from pydantic import BaseModel, ConfigDict, Field

from .PredictionTiming import PredictionTiming


class Prediction(BaseModel):
    id: str | None = Field(None)
    operationType: int | None = Field(None)
    vehicleId: str | None = Field(None)
    naptanId: str | None = Field(None)
    stationName: str | None = Field(None)
    lineId: str | None = Field(None)
    lineName: str | None = Field(None)
    platformName: str | None = Field(None)
    direction: str | None = Field(None)
    bearing: str | None = Field(None)
    destinationNaptanId: str | None = Field(None)
    destinationName: str | None = Field(None)
    timestamp: str | None = Field(None)
    timeToStation: int | None = Field(None)
    currentLocation: str | None = Field(None)
    towards: str | None = Field(None)
    expectedArrival: str | None = Field(None)
    timeToLive: str | None = Field(None)
    modeName: str | None = Field(None)
    timing: PredictionTiming | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
