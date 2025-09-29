from pydantic import BaseModel, ConfigDict, Field

from .Schedule import Schedule
from .StationInterval import StationInterval


class TimetableRoute(BaseModel):
    stationIntervals: list[StationInterval] | None = Field(None)
    schedules: list[Schedule] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
