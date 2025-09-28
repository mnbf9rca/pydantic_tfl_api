from pydantic import BaseModel, Field, ConfigDict


class ServiceFrequency(BaseModel):
    lowestFrequency: float | None = Field(None)
    highestFrequency: float | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
