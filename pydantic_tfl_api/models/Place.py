from pydantic import BaseModel, ConfigDict, Field

from .AdditionalProperties import AdditionalProperties


class Place(BaseModel):
    id: str | None = Field(None)
    url: str | None = Field(None)
    commonName: str | None = Field(None)
    distance: float | None = Field(None)
    placeType: str | None = Field(None)
    additionalProperties: list[AdditionalProperties] | None = Field(None)
    children: list['Place'] | None = Field(None)
    childrenUrls: list[str] | None = Field(None)
    lat: float | None = Field(None)
    lon: float | None = Field(None)

    model_config = ConfigDict(from_attributes=True)

Place.model_rebuild()
