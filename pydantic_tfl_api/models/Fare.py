from .FareTap import FareTap
from pydantic import BaseModel, Field, ConfigDict


class Fare(BaseModel):
    lowZone: int | None = Field(None)
    highZone: int | None = Field(None)
    cost: int | None = Field(None)
    chargeProfileName: str | None = Field(None)
    isHopperFare: bool | None = Field(None)
    chargeLevel: str | None = Field(None)
    peak: int | None = Field(None)
    offPeak: int | None = Field(None)
    taps: list[FareTap] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
