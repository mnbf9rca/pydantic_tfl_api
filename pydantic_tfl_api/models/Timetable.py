from .TimetableRoute import TimetableRoute
from pydantic import BaseModel, Field, ConfigDict


class Timetable(BaseModel):
    departureStopId: str | None = Field(None)
    routes: list[TimetableRoute] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
