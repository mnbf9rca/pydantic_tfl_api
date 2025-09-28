from .Bay import Bay
from pydantic import BaseModel, Field, ConfigDict


class CarParkOccupancy(BaseModel):
    id: str | None = Field(None)
    bays: list[Bay] | None = Field(None)
    name: str | None = Field(None)
    carParkDetailsUrl: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
