from .AdditionalProperties import AdditionalProperties
from pydantic import BaseModel, Field
from typing import List, Optional


class Place(BaseModel):
    id: Optional[str] = Field(None, alias='id')
    url: Optional[str] = Field(None, alias='url')
    commonName: Optional[str] = Field(None, alias='commonName')
    distance: Optional[float] = Field(None, alias='distance')
    placeType: Optional[str] = Field(None, alias='placeType')
    additionalProperties: Optional[list[AdditionalProperties]] = Field(None, alias='additionalProperties')
    children: Optional[list['Place']] = Field(None, alias='children')
    childrenUrls: Optional[list[str]] = Field(None, alias='childrenUrls')
    lat: Optional[float] = Field(None, alias='lat')
    lon: Optional[float] = Field(None, alias='lon')

    model_config = {'from_attributes': True}

Place.model_rebuild()
