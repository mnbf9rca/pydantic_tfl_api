from .Fare import Fare
from .FareCaveat import FareCaveat
from pydantic import BaseModel, Field
from typing import List, Optional


class JourneyFare(BaseModel):
    totalCost: Optional[int] = Field(None, alias='totalCost')
    fares: Optional[list[Fare]] = Field(None, alias='fares')
    caveats: Optional[list[FareCaveat]] = Field(None, alias='caveats')

    model_config = {'from_attributes': True}
