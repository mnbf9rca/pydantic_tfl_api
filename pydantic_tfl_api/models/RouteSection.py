from pydantic import BaseModel, ConfigDict, Field

from .RouteSectionNaptanEntrySequence import RouteSectionNaptanEntrySequence


class RouteSection(BaseModel):
    id: str | None = Field(None)
    lineId: str | None = Field(None)
    routeCode: str | None = Field(None)
    name: str | None = Field(None)
    lineString: str | None = Field(None)
    direction: str | None = Field(None)
    originationName: str | None = Field(None)
    destinationName: str | None = Field(None)
    validTo: str | None = Field(None)
    validFrom: str | None = Field(None)
    routeSectionNaptanEntrySequence: list[RouteSectionNaptanEntrySequence] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
