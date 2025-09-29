from pydantic import BaseModel, ConfigDict, Field


class TimeAdjustment(BaseModel):
    date: str | None = Field(None)
    time: str | None = Field(None)
    timeIs: str | None = Field(None)
    uri: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
