from .Schedule import Schedule
from .StationInterval import StationInterval
from pydantic import BaseModel, Field
from typing import List, Optional


class TimetableRoute(BaseModel):
    stationIntervals: Optional[list[StationInterval]] = Field(None, alias='stationIntervals')
    schedules: Optional[list[Schedule]] = Field(None, alias='schedules')

    model_config = {'from_attributes': True}
