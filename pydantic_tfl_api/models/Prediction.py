from pydantic import BaseModel, ConfigDict, Field

from .PredictionTiming import PredictionTiming


class Prediction(BaseModel):
    """DTO to capture the prediction details"""

    id: str | None = Field(None, description="The identitier for the prediction")
    operationType: int | None = Field(None, description="The type of the operation (1: is new or has been updated, 2: should be deleted from any client cache)")
    vehicleId: str | None = Field(None, description="The actual vehicle in transit (for train modes, the leading car of the rolling set)")
    naptanId: str | None = Field(None, description="Identifier for the prediction")
    stationName: str | None = Field(None, description="Station name")
    lineId: str | None = Field(None, description="Unique identifier for the Line")
    lineName: str | None = Field(None, description="Line Name")
    platformName: str | None = Field(None, description="Platform name (for bus, this is the stop letter)")
    direction: str | None = Field(None, description="Direction (unified to inbound/outbound)")
    bearing: str | None = Field(None, description="Bearing (between 0 to 359)")
    destinationNaptanId: str | None = Field(None, description="Naptan Identifier for the prediction's destination")
    destinationName: str | None = Field(None, description="Name of the destination")
    timestamp: str | None = Field(None, description="Timestamp for when the prediction was inserted/modified (source column drives what objects are broadcast on each iteration)")
    timeToStation: int | None = Field(None, description="Prediction of the Time to station in seconds")
    currentLocation: str | None = Field(None, description="The current location of the vehicle.")
    towards: str | None = Field(None, description="Routing information or other descriptive text about the path of the vehicle towards the destination")
    expectedArrival: str | None = Field(None, description="The expected arrival time of the vehicle at the stop/station")
    timeToLive: str | None = Field(None, description="The expiry time for the prediction")
    modeName: str | None = Field(None, description="The mode name of the station/line the prediction relates to")
    timing: PredictionTiming | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
