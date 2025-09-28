from .Schedule import Schedule
from .StationInterval import StationInterval
from pydantic import BaseModel, Field, ConfigDict


class TimetableRoute(BaseModel):
    stationIntervals: list[StationInterval] | None = Field(None)
    schedules: list[Schedule] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
