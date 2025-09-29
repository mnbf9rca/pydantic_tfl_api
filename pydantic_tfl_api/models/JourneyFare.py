from pydantic import BaseModel, ConfigDict, Field

from .Fare import Fare
from .FareCaveat import FareCaveat


class JourneyFare(BaseModel):
    totalCost: int | None = Field(None)
    fares: list[Fare] | None = Field(None)
    caveats: list[FareCaveat] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
