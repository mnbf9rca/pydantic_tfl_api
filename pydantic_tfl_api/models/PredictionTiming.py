from pydantic import BaseModel, Field, ConfigDict


class PredictionTiming(BaseModel):
    countdownServerAdjustment: str | None = Field(None)
    source: str | None = Field(None)
    insert: str | None = Field(None)
    read: str | None = Field(None)
    sent: str | None = Field(None)
    received: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
