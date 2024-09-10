from .FareTap import FareTap
from pydantic import BaseModel, Field
from typing import List, Optional


class Fare(BaseModel):
    lowZone: Optional[int] = Field(None, alias='lowZone')
    highZone: Optional[int] = Field(None, alias='highZone')
    cost: Optional[int] = Field(None, alias='cost')
    chargeProfileName: Optional[str] = Field(None, alias='chargeProfileName')
    isHopperFare: Optional[bool] = Field(None, alias='isHopperFare')
    chargeLevel: Optional[str] = Field(None, alias='chargeLevel')
    peak: Optional[int] = Field(None, alias='peak')
    offPeak: Optional[int] = Field(None, alias='offPeak')
    taps: Optional[list[FareTap]] = Field(None, alias='taps')

    model_config = {'from_attributes': True}
