from pydantic import BaseModel, ConfigDict, Field


class RoadDisruptionSchedule(BaseModel):
    startTime: str | None = Field(None)
    endTime: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
