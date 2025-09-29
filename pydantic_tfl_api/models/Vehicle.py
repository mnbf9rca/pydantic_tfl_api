from pydantic import BaseModel, ConfigDict, Field


class Vehicle(BaseModel):
    type: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
