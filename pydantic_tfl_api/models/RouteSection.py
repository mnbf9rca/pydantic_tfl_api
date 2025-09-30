from pydantic import BaseModel, ConfigDict, Field

from .RouteSectionNaptanEntrySequence import RouteSectionNaptanEntrySequence


class RouteSection(BaseModel):
    id: str | None = Field(None, description="The Id of the route")
    lineId: str | None = Field(None, description="The Id of the Line")
    routeCode: str | None = Field(None, description="The route code")
    name: str | None = Field(None, description="Name such as \"72\"")
    lineString: str | None = Field(None, description="The co-ordinates of the route's path as a geoJSON lineString")
    direction: str | None = Field(None, description="Inbound or Outbound")
    originationName: str | None = Field(None, description="The name of the Origin StopPoint")
    destinationName: str | None = Field(None, description="The name of the Destination StopPoint")
    validTo: str | None = Field(None, description="The DateTime that the Service containing this Route is valid until.")
    validFrom: str | None = Field(None, description="The DateTime that the Service containing this Route is valid from.")
    routeSectionNaptanEntrySequence: list[RouteSectionNaptanEntrySequence] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
