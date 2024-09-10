from .Disruption import Disruption
from .Identifier import Identifier
from .Instruction import Instruction
from .Obstacle import Obstacle
from .Path import Path
from .PlannedWork import PlannedWork
from .Point import Point
from .RouteOption import RouteOption
from pydantic import BaseModel, Field
from typing import List, Optional


class Leg(BaseModel):
    duration: Optional[int] = Field(None, alias='duration')
    speed: Optional[str] = Field(None, alias='speed')
    instruction: Optional[Instruction] = Field(None, alias='instruction')
    obstacles: Optional[list[Obstacle]] = Field(None, alias='obstacles')
    departureTime: Optional[str] = Field(None, alias='departureTime')
    arrivalTime: Optional[str] = Field(None, alias='arrivalTime')
    departurePoint: Optional[Point] = Field(None, alias='departurePoint')
    arrivalPoint: Optional[Point] = Field(None, alias='arrivalPoint')
    path: Optional[Path] = Field(None, alias='path')
    routeOptions: Optional[list[RouteOption]] = Field(None, alias='routeOptions')
    mode: Optional[Identifier] = Field(None, alias='mode')
    disruptions: Optional[list[Disruption]] = Field(None, alias='disruptions')
    plannedWorks: Optional[list[PlannedWork]] = Field(None, alias='plannedWorks')
    distance: Optional[float] = Field(None, alias='distance')
    isDisrupted: Optional[bool] = Field(None, alias='isDisrupted')
    hasFixedLocations: Optional[bool] = Field(None, alias='hasFixedLocations')

    model_config = {'from_attributes': True}
