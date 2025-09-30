from pydantic import BaseModel, ConfigDict, Field

from .AdditionalProperties import AdditionalProperties


class Place(BaseModel):
    id: str | None = Field(None, description="A unique identifier.")
    url: str | None = Field(None, description="The unique location of this resource.")
    commonName: str | None = Field(None, description="A human readable name.")
    distance: float | None = Field(None, description="The distance of the place from its search point, if this is the result of a geographical search, otherwise zero.")
    placeType: str | None = Field(None, description="The type of Place. See /Place/Meta/placeTypes for possible values.")
    additionalProperties: list[AdditionalProperties] | None = Field(None, description="A bag of additional key/value pairs with extra information about this place.")
    children: list['Place'] | None = Field(None)
    childrenUrls: list[str] | None = Field(None)
    lat: float | None = Field(None, description="WGS84 latitude of the location.")
    lon: float | None = Field(None, description="WGS84 longitude of the location.")

    model_config = ConfigDict(from_attributes=True)

Place.model_rebuild()
