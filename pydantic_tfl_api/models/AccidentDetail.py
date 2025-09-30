from pydantic import BaseModel, ConfigDict, Field

from .Casualty import Casualty
from .Vehicle import Vehicle


class AccidentDetail(BaseModel):
    id: int | None = Field(None)
    lat: float | None = Field(None)
    lon: float | None = Field(None)
    location: str | None = Field(None)
    date: str | None = Field(None)
    severity: str | None = Field(None)
    borough: str | None = Field(None)
    casualties: list[Casualty] | None = Field(None)
    vehicles: list[Vehicle] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
