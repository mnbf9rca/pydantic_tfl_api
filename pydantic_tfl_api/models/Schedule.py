from .KnownJourney import KnownJourney
from .Period import Period
from pydantic import BaseModel, Field
from typing import List, Optional


class Schedule(BaseModel):
    name: Optional[str] = Field(None, alias='name')
    knownJourneys: Optional[list[KnownJourney]] = Field(None, alias='knownJourneys')
    firstJourney: Optional[KnownJourney] = Field(None, alias='firstJourney')
    lastJourney: Optional[KnownJourney] = Field(None, alias='lastJourney')
    periods: Optional[list[Period]] = Field(None, alias='periods')

    model_config = {'from_attributes': True}
