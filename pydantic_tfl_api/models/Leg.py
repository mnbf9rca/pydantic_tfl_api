from pydantic import BaseModel, ConfigDict, Field

from .Disruption import Disruption
from .Identifier import Identifier
from .Instruction import Instruction
from .Obstacle import Obstacle
from .Path import Path
from .PlannedWork import PlannedWork
from .Point import Point
from .RouteOption import RouteOption


class Leg(BaseModel):
    duration: int | None = Field(None)
    speed: str | None = Field(None)
    instruction: Instruction | None = Field(None)
    obstacles: list[Obstacle] | None = Field(None)
    departureTime: str | None = Field(None)
    arrivalTime: str | None = Field(None)
    departurePoint: Point | None = Field(None)
    arrivalPoint: Point | None = Field(None)
    path: Path | None = Field(None)
    routeOptions: list[RouteOption] | None = Field(None)
    mode: Identifier | None = Field(None)
    disruptions: list[Disruption] | None = Field(None)
    plannedWorks: list[PlannedWork] | None = Field(None)
    distance: float | None = Field(None)
    isDisrupted: bool | None = Field(None)
    hasFixedLocations: bool | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
