from pydantic import BaseModel, ConfigDict, Field

from .Interval import Interval


class StationInterval(BaseModel):
    id: str | None = Field(None)
    intervals: list[Interval] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
