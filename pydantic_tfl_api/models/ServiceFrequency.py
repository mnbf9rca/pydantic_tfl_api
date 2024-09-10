from pydantic import BaseModel, Field
from typing import Optional


class ServiceFrequency(BaseModel):
    lowestFrequency: Optional[float] = Field(None, alias='lowestFrequency')
    highestFrequency: Optional[float] = Field(None, alias='highestFrequency')

    model_config = {'from_attributes': True}
