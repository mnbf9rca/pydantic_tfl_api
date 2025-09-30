from pydantic import BaseModel, ConfigDict, Field


class JpElevation(BaseModel):
    distance: int | None = Field(None)
    startLat: float | None = Field(None)
    startLon: float | None = Field(None)
    endLat: float | None = Field(None)
    endLon: float | None = Field(None)
    heightFromPreviousPoint: int | None = Field(None)
    gradient: float | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
