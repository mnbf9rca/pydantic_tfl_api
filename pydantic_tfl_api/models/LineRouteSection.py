from pydantic import BaseModel, Field
from typing import Optional


class LineRouteSection(BaseModel):
    routeId: Optional[int] = Field(None, alias='routeId')
    direction: Optional[str] = Field(None, alias='direction')
    destination: Optional[str] = Field(None, alias='destination')
    fromStation: Optional[str] = Field(None, alias='fromStation')
    toStation: Optional[str] = Field(None, alias='toStation')
    serviceType: Optional[str] = Field(None, alias='serviceType')
    vehicleDestinationText: Optional[str] = Field(None, alias='vehicleDestinationText')

    model_config = {'from_attributes': True}
