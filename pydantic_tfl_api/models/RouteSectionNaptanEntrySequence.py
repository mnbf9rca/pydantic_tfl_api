from .StopPoint import StopPoint
from pydantic import BaseModel, Field, ConfigDict


class RouteSectionNaptanEntrySequence(BaseModel):
    ordinal: int | None = Field(None)
    stopPoint: StopPoint | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
