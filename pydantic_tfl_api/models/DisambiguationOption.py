from pydantic import BaseModel, ConfigDict, Field


class DisambiguationOption(BaseModel):
    description: str | None = Field(None)
    uri: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
