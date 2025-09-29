from .JourneyFare import JourneyFare
from .Leg import Leg
from pydantic import BaseModel, Field, ConfigDict


class Journey(BaseModel):
    startDateTime: str | None = Field(None)
    duration: int | None = Field(None)
    arrivalDateTime: str | None = Field(None)
    legs: list[Leg] | None = Field(None)
    fare: JourneyFare | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
