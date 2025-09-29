from pydantic import BaseModel, ConfigDict, Field

from .DbGeographyWellKnownValue import DbGeographyWellKnownValue


class DbGeography(BaseModel):
    geography: DbGeographyWellKnownValue | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
