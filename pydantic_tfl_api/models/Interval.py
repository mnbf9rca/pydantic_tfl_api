from pydantic import BaseModel, ConfigDict, Field


class Interval(BaseModel):
    stopId: str | None = Field(None)
    timeToArrival: float | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
