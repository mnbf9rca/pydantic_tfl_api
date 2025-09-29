from pydantic import BaseModel, ConfigDict, Field


class KnownJourney(BaseModel):
    hour: str | None = Field(None)
    minute: str | None = Field(None)
    intervalId: int | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
