from pydantic import BaseModel, Field, ConfigDict


class RoadDisruptionSchedule(BaseModel):
    startTime: str | None = Field(None)
    endTime: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
