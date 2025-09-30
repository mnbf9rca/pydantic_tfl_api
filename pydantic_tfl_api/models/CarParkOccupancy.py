from pydantic import BaseModel, ConfigDict, Field

from .Bay import Bay


class CarParkOccupancy(BaseModel):
    id: str | None = Field(None)
    bays: list[Bay] | None = Field(None)
    name: str | None = Field(None)
    carParkDetailsUrl: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
