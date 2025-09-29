from pydantic import BaseModel, ConfigDict, Field


class JourneyVector(BaseModel):
    from_field: str | None = Field(None, alias='from')
    to: str | None = Field(None)
    via: str | None = Field(None)
    uri: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
