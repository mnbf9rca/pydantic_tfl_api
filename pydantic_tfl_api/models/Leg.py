from .Disruption import Disruption
from .Identifier import Identifier
from .Instruction import Instruction
from .Obstacle import Obstacle
from .Path import Path
from .PlannedWork import PlannedWork
from .Point import Point
from .RouteOption import RouteOption
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class Leg(BaseModel):
    duration: int | None = Field(None)
    speed: str | None = Field(None)
    instruction: Optional[Instruction] = Field(None)
    obstacles: list[Obstacle] | None = Field(None)
    departureTime: str | None = Field(None)
    arrivalTime: str | None = Field(None)
    departurePoint: Optional[Point] = Field(None)
    arrivalPoint: Optional[Point] = Field(None)
    path: Optional[Path] = Field(None)
    routeOptions: list[RouteOption] | None = Field(None)
    mode: Optional[Identifier] = Field(None)
    disruptions: list[Disruption] | None = Field(None)
    plannedWorks: list[PlannedWork] | None = Field(None)
    distance: float | None = Field(None)
    isDisrupted: bool | None = Field(None)
    hasFixedLocations: bool | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
