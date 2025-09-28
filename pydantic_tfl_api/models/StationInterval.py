from .Interval import Interval
from pydantic import BaseModel, Field, ConfigDict


class StationInterval(BaseModel):
    id: str | None = Field(None)
    intervals: list[Interval] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
