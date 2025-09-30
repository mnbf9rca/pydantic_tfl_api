from pydantic import BaseModel, ConfigDict, Field

from .KnownJourney import KnownJourney
from .Period import Period


class Schedule(BaseModel):
    name: str | None = Field(None)
    knownJourneys: list[KnownJourney] | None = Field(None)
    firstJourney: KnownJourney | None = Field(None)
    lastJourney: KnownJourney | None = Field(None)
    periods: list[Period] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
