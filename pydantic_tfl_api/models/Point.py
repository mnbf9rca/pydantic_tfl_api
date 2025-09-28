from pydantic import BaseModel, Field, ConfigDict


class Point(BaseModel):
    lat: float | None = Field(None)
    lon: float | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
