from .Disambiguation import Disambiguation
from .MatchedStop import MatchedStop
from .Timetable import Timetable
from pydantic import BaseModel, Field
from typing import List, Match, Optional


class TimetableResponse(BaseModel):
    lineId: Optional[str] = Field(None, alias='lineId')
    lineName: Optional[str] = Field(None, alias='lineName')
    direction: Optional[str] = Field(None, alias='direction')
    pdfUrl: Optional[str] = Field(None, alias='pdfUrl')
    stations: Optional[list[MatchedStop]] = Field(None, alias='stations')
    stops: Optional[list[MatchedStop]] = Field(None, alias='stops')
    timetable: Optional[Timetable] = Field(None, alias='timetable')
    disambiguation: Optional[Disambiguation] = Field(None, alias='disambiguation')
    statusErrorMessage: Optional[str] = Field(None, alias='statusErrorMessage')

    model_config = {'from_attributes': True}
