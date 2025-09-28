from pydantic import BaseModel, Field, ConfigDict


class Mode(BaseModel):
    isTflService: bool | None = Field(None)
    isFarePaying: bool | None = Field(None)
    isScheduledService: bool | None = Field(None)
    modeName: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
