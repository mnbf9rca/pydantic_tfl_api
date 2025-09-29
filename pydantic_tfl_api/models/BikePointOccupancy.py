from pydantic import BaseModel, ConfigDict, Field


class BikePointOccupancy(BaseModel):
    id: str | None = Field(None)
    name: str | None = Field(None)
    bikesCount: int | None = Field(None)
    emptyDocks: int | None = Field(None)
    totalDocks: int | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
