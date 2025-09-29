from .DbGeographyWellKnownValue import DbGeographyWellKnownValue
from pydantic import BaseModel, Field, ConfigDict


class DbGeography(BaseModel):
    geography: DbGeographyWellKnownValue | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
