from pydantic import BaseModel, ConfigDict, Field


class BikePointOccupancy(BaseModel):
    """Bike point occupancy"""

    id: str | None = Field(None, description="Id of the bike point such as BikePoints_1")
    name: str | None = Field(None, description="Name / Common name of the bike point")
    bikesCount: int | None = Field(None, description="Total bike counts")
    emptyDocks: int | None = Field(None, description="Empty docks")
    totalDocks: int | None = Field(None, description="Total docks available")

    model_config = ConfigDict(from_attributes=True)
