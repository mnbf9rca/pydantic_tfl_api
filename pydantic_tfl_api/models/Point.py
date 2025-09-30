from pydantic import BaseModel, ConfigDict, Field


class Point(BaseModel):
    """Represents a point located at a latitude and longitude using the WGS84 co-ordinate system."""

    lat: float | None = Field(None, description="WGS84 latitude of the location.")
    lon: float | None = Field(None, description="WGS84 longitude of the location.")

    model_config = ConfigDict(from_attributes=True)
