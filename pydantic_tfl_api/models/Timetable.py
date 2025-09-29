from pydantic import BaseModel, ConfigDict, Field

from .TimetableRoute import TimetableRoute


class Timetable(BaseModel):
    departureStopId: str | None = Field(None)
    routes: list[TimetableRoute] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
