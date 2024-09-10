from pydantic import BaseModel, Field
from typing import Optional


class MatchedRoute(BaseModel):
    routeCode: Optional[str] = Field(None, alias='routeCode')
    name: Optional[str] = Field(None, alias='name')
    direction: Optional[str] = Field(None, alias='direction')
    originationName: Optional[str] = Field(None, alias='originationName')
    destinationName: Optional[str] = Field(None, alias='destinationName')
    originator: Optional[str] = Field(None, alias='originator')
    destination: Optional[str] = Field(None, alias='destination')
    serviceType: Optional[str] = Field(None, alias='serviceType')
    validTo: Optional[str] = Field(None, alias='validTo')
    validFrom: Optional[str] = Field(None, alias='validFrom')

    model_config = {'from_attributes': True}
