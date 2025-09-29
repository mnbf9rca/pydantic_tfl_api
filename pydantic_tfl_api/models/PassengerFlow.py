from pydantic import BaseModel, ConfigDict, Field


class PassengerFlow(BaseModel):
    timeSlice: str | None = Field(None)
    value: int | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
