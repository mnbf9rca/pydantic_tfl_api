from .DbGeographyWellKnownValue import DbGeographyWellKnownValue
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class DbGeography(BaseModel):
    geography: Optional[DbGeographyWellKnownValue] = Field(None)

    model_config = ConfigDict(from_attributes=True)
