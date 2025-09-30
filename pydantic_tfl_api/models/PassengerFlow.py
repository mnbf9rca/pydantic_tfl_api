from pydantic import BaseModel, ConfigDict, Field


class PassengerFlow(BaseModel):
    timeSlice: str | None = Field(None, description="Time in 24hr format with 15 minute intervals e.g. 0500-0515, 0515-0530 etc.")
    value: int | None = Field(None, description="Count of passenger flow towards a platform")

    model_config = ConfigDict(from_attributes=True)
