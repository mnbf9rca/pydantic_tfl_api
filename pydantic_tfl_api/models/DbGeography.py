from pydantic import BaseModel, Field
from .DbGeographyWellKnownValue import DbGeographyWellKnownValue
from pydantic import BaseModel, Field
from typing import Optional


class DbGeography(BaseModel):
    geography: Optional[DbGeographyWellKnownValue] = Field(None, alias='geography')

    class Config:
        from_attributes = True
