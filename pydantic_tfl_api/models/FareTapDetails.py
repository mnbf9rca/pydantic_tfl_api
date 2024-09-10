from pydantic import BaseModel, Field
from typing import Optional


class FareTapDetails(BaseModel):
    modeType: Optional[str] = Field(None, alias='modeType')
    validationType: Optional[str] = Field(None, alias='validationType')
    hostDeviceType: Optional[str] = Field(None, alias='hostDeviceType')
    busRouteId: Optional[str] = Field(None, alias='busRouteId')
    nationalLocationCode: Optional[int] = Field(None, alias='nationalLocationCode')
    tapTimestamp: Optional[str] = Field(None, alias='tapTimestamp')

    model_config = {'from_attributes': True}
