from .RouteSectionNaptanEntrySequence import RouteSectionNaptanEntrySequence
from pydantic import BaseModel, Field
from typing import List, Optional, Sequence


class RouteSection(BaseModel):
    id: Optional[str] = Field(None, alias='id')
    lineId: Optional[str] = Field(None, alias='lineId')
    routeCode: Optional[str] = Field(None, alias='routeCode')
    name: Optional[str] = Field(None, alias='name')
    lineString: Optional[str] = Field(None, alias='lineString')
    direction: Optional[str] = Field(None, alias='direction')
    originationName: Optional[str] = Field(None, alias='originationName')
    destinationName: Optional[str] = Field(None, alias='destinationName')
    validTo: Optional[str] = Field(None, alias='validTo')
    validFrom: Optional[str] = Field(None, alias='validFrom')
    routeSectionNaptanEntrySequence: Optional[list[RouteSectionNaptanEntrySequence]] = Field(None, alias='routeSectionNaptanEntrySequence')

    model_config = {'from_attributes': True}
