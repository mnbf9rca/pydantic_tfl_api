from pydantic import BaseModel, ConfigDict, Field


class Point(BaseModel):
    lat: float | None = Field(None)
    lon: float | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
