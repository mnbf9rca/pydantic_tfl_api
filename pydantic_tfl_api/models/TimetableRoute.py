from pydantic import BaseModel, Field
from .Schedule import Schedule
from .StationInterval import StationInterval
from pydantic import BaseModel, Field
from typing import List, Optional


class TimetableRoute(BaseModel):
    stationIntervals: Optional[List[StationInterval]] = Field(None, alias='stationIntervals')
    schedules: Optional[List[Schedule]] = Field(None, alias='schedules')

    class Config:
        from_attributes = True
