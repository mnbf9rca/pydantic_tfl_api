from pydantic import BaseModel, Field
from typing import Optional


class SearchMatch(BaseModel):
    id: Optional[str] = Field(None, alias='id')
    url: Optional[str] = Field(None, alias='url')
    name: Optional[str] = Field(None, alias='name')
    lat: Optional[float] = Field(None, alias='lat')
    lon: Optional[float] = Field(None, alias='lon')

    model_config = {'from_attributes': True}
