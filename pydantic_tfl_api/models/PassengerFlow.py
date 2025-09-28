from pydantic import BaseModel, Field, ConfigDict


class PassengerFlow(BaseModel):
    timeSlice: str | None = Field(None)
    value: int | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
