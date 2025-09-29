from .StopPoint import StopPoint
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class RouteSectionNaptanEntrySequence(BaseModel):
    ordinal: int | None = Field(None)
    stopPoint: Optional[StopPoint] = Field(None)

    model_config = ConfigDict(from_attributes=True)
