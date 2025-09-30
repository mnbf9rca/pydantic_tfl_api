from pydantic import BaseModel, ConfigDict, Field

from .StopPoint import StopPoint


class StopPointsResponse(BaseModel):
    """A paged response containing StopPoints"""

    centrePoint: list[float] | None = Field(None, description="The centre latitude/longitude of this list of StopPoints")
    stopPoints: list[StopPoint] | None = Field(None, description="Collection of stop points")
    pageSize: int | None = Field(None, description="The maximum size of the page in this response i.e. the maximum number of StopPoints")
    total: int | None = Field(None, description="The total number of StopPoints available across all pages")
    page: int | None = Field(None, description="The index of this page")

    model_config = ConfigDict(from_attributes=True)
