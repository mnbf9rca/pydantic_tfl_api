from pydantic import BaseModel, Field
from typing import Optional


class StopPointRouteSection(BaseModel):
    naptanId: Optional[str] = Field(None, alias='naptanId')
    lineId: Optional[str] = Field(None, alias='lineId')
    mode: Optional[str] = Field(None, alias='mode')
    validFrom: Optional[str] = Field(None, alias='validFrom')
    validTo: Optional[str] = Field(None, alias='validTo')
    direction: Optional[str] = Field(None, alias='direction')
    routeSectionName: Optional[str] = Field(None, alias='routeSectionName')
    lineString: Optional[str] = Field(None, alias='lineString')
    isActive: Optional[bool] = Field(None, alias='isActive')
    serviceType: Optional[str] = Field(None, alias='serviceType')
    vehicleDestinationText: Optional[str] = Field(None, alias='vehicleDestinationText')
    destinationName: Optional[str] = Field(None, alias='destinationName')

    model_config = {'from_attributes': True}
