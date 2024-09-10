from pydantic import BaseModel, Field
from typing import Optional


class Point(BaseModel):
    lat: Optional[float] = Field(None, alias='lat')
    lon: Optional[float] = Field(None, alias='lon')

    model_config = {'from_attributes': True}
