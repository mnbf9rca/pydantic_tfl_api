from pydantic import BaseModel, Field
from .TimetableRoute import TimetableRoute
from pydantic import BaseModel, Field
from typing import List, Optional


class Timetable(BaseModel):
    departureStopId: Optional[str] = Field(None, alias='departureStopId')
    routes: Optional[List[TimetableRoute]] = Field(None, alias='routes')

    class Config:
        from_attributes = True
