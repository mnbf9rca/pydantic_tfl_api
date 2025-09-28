from .Disambiguation import Disambiguation
from .MatchedStop import MatchedStop
from .Timetable import Timetable
from pydantic import BaseModel, Field, ConfigDict
from typing import Match


class TimetableResponse(BaseModel):
    lineId: str | None = Field(None)
    lineName: str | None = Field(None)
    direction: str | None = Field(None)
    pdfUrl: str | None = Field(None)
    stations: list[MatchedStop] | None = Field(None)
    stops: list[MatchedStop] | None = Field(None)
    timetable: Timetable | None = Field(None)
    disambiguation: Disambiguation | None = Field(None)
    statusErrorMessage: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
