from pydantic import BaseModel, Field, ConfigDict


class DbGeographyWellKnownValue(BaseModel):
    coordinateSystemId: int | None = Field(None)
    wellKnownText: str | None = Field(None)
    wellKnownBinary: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
