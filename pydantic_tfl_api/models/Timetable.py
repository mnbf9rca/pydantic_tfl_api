from .TimetableRoute import TimetableRoute
from pydantic import BaseModel, Field
from typing import List, Optional


class Timetable(BaseModel):
    departureStopId: Optional[str] = Field(None, alias='departureStopId')
    routes: Optional[list[TimetableRoute]] = Field(None, alias='routes')

    model_config = {'from_attributes': True}
