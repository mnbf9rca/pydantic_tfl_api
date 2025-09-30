from pydantic import BaseModel, ConfigDict, Field

from .JourneyFare import JourneyFare
from .Leg import Leg


class Journey(BaseModel):
    """Object that represents an end to end journey (see schematic)."""

    startDateTime: str | None = Field(None)
    duration: int | None = Field(None)
    arrivalDateTime: str | None = Field(None)
    legs: list[Leg] | None = Field(None)
    fare: JourneyFare | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
