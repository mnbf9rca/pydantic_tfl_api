from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
from typing import Optional


class DbGeographyWellKnownValue(BaseModel):
    coordinateSystemId: Optional[int] = Field(None, alias='coordinateSystemId')
    wellKnownText: Optional[str] = Field(None, alias='wellKnownText')
    wellKnownBinary: Optional[str] = Field(None, alias='wellKnownBinary')

    class Config:
        from_attributes = True
