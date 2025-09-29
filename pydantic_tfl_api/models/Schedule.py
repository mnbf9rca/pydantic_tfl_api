from .KnownJourney import KnownJourney
from .Period import Period
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class Schedule(BaseModel):
    name: str | None = Field(None)
    knownJourneys: list[KnownJourney] | None = Field(None)
    firstJourney: Optional[KnownJourney] = Field(None)
    lastJourney: Optional[KnownJourney] = Field(None)
    periods: list[Period] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
