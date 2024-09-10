from .JourneyFare import JourneyFare
from .Leg import Leg
from pydantic import BaseModel, Field
from typing import List, Optional


class Journey(BaseModel):
    startDateTime: Optional[str] = Field(None, alias='startDateTime')
    duration: Optional[int] = Field(None, alias='duration')
    arrivalDateTime: Optional[str] = Field(None, alias='arrivalDateTime')
    legs: Optional[list[Leg]] = Field(None, alias='legs')
    fare: Optional[JourneyFare] = Field(None, alias='fare')

    model_config = {'from_attributes': True}
