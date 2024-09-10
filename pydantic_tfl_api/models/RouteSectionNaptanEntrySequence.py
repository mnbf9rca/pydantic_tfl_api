from .StopPoint import StopPoint
from pydantic import BaseModel, Field
from typing import Optional


class RouteSectionNaptanEntrySequence(BaseModel):
    ordinal: Optional[int] = Field(None, alias='ordinal')
    stopPoint: Optional[StopPoint] = Field(None, alias='stopPoint')

    model_config = {'from_attributes': True}
