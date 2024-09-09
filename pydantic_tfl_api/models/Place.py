from pydantic import BaseModel, Field
from .AdditionalProperties import AdditionalProperties
from pydantic import BaseModel, Field
from typing import ForwardRef


class Place(BaseModel):
    id: str = Field(None, alias='id')
    url: str = Field(None, alias='url')
    commonName: str = Field(None, alias='commonName')
    distance: float = Field(None, alias='distance')
    placeType: str = Field(None, alias='placeType')
    additionalProperties: AdditionalProperties = Field(None, alias='additionalProperties')
    children: 'Place' = Field(None, alias='children')
    childrenUrls: str = Field(None, alias='childrenUrls')
    lat: float = Field(None, alias='lat')
    lon: float = Field(None, alias='lon')

    class Config:
        from_attributes = True

Place.model_rebuild()
