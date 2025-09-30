from pydantic import BaseModel, ConfigDict, Field

from .StopPoint import StopPoint


class StopPointsResponse(BaseModel):
    centrePoint: list[float] | None = Field(None)
    stopPoints: list[StopPoint] | None = Field(None)
    pageSize: int | None = Field(None)
    total: int | None = Field(None)
    page: int | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
