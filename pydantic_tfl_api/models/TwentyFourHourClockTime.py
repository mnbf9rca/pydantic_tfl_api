from pydantic import BaseModel, Field, ConfigDict


class TwentyFourHourClockTime(BaseModel):
    hour: str | None = Field(None)
    minute: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
