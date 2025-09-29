from pydantic import BaseModel, ConfigDict, Field

from .StopPoint import StopPoint


class RouteSectionNaptanEntrySequence(BaseModel):
    ordinal: int | None = Field(None)
    stopPoint: StopPoint | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
