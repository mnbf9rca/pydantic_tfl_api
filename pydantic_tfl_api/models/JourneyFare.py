from pydantic import BaseModel, Field
from .Fare import Fare
from .FareCaveat import FareCaveat
from pydantic import BaseModel, Field
from typing import List, Optional


class JourneyFare(BaseModel):
    totalCost: Optional[int] = Field(None, alias='totalCost')
    fares: Optional[List[Fare]] = Field(None, alias='fares')
    caveats: Optional[List[FareCaveat]] = Field(None, alias='caveats')

    class Config:
        from_attributes = True
