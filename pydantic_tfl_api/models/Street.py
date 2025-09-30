from pydantic import BaseModel, ConfigDict, Field

from .StreetSegment import StreetSegment


class Street(BaseModel):
    name: str | None = Field(None, description="Street name")
    closure: str | None = Field(None, description="Type of road closure. Some example values: Open = road is open, not blocked, not closed, not restricted. It maybe that the disruption has been moved out of the carriageway. Partial Closure = road is partially blocked, closed or restricted. Full Closure = road is fully blocked or closed.")
    directions: str | None = Field(None, description="The direction of the disruption on the street. Some example values: All Directions All Approaches Clockwise Anti-Clockwise Northbound Eastbound Southbound Westbound Both Directions")
    segments: list[StreetSegment] | None = Field(None, description="Geographic description of the sections of this street that are affected.")
    sourceSystemId: int | None = Field(None, description="The ID from the source system of the disruption that this street belongs to.")
    sourceSystemKey: str | None = Field(None, description="The key of the source system of the disruption that this street belongs to.")

    model_config = ConfigDict(from_attributes=True)
