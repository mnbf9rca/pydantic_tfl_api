from pydantic import BaseModel, ConfigDict, Field


class FareCaveat(BaseModel):
    text: str | None = Field(None)
    type: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
