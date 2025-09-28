from pydantic import BaseModel, Field, ConfigDict


class Vehicle(BaseModel):
    type: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
