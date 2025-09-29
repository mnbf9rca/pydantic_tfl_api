from .AdditionalProperties import AdditionalProperties
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class Place(BaseModel):
    id: Optional[str] = Field(None)
    url: Optional[str] = Field(None)
    commonName: Optional[str] = Field(None)
    distance: Optional[float] = Field(None)
    placeType: Optional[str] = Field(None)
    additionalProperties: Optional[list[AdditionalProperties]] = Field(None)
    children: Optional[list['Place']] = Field(None)
    childrenUrls: Optional[list[str]] = Field(None)
    lat: Optional[float] = Field(None)
    lon: Optional[float] = Field(None)

    model_config = ConfigDict(from_attributes=True)

Place.model_rebuild()
