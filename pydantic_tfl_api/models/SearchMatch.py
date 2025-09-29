from pydantic import BaseModel, ConfigDict, Field


class SearchMatch(BaseModel):
    id: str | None = Field(None)
    url: str | None = Field(None)
    name: str | None = Field(None)
    lat: float | None = Field(None)
    lon: float | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
