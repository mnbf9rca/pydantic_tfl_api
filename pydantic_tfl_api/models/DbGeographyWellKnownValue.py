from pydantic import BaseModel, Field
from typing import Optional


class DbGeographyWellKnownValue(BaseModel):
    coordinateSystemId: Optional[int] = Field(None, alias='coordinateSystemId')
    wellKnownText: Optional[str] = Field(None, alias='wellKnownText')
    wellKnownBinary: Optional[str] = Field(None, alias='wellKnownBinary')

    model_config = {'from_attributes': True}
