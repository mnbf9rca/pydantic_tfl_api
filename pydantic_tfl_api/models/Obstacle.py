from pydantic import BaseModel, Field, ConfigDict


class Obstacle(BaseModel):
    type: str | None = Field(None)
    incline: str | None = Field(None)
    stopId: int | None = Field(None)
    position: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
