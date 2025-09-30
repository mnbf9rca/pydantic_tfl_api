from pydantic import BaseModel, ConfigDict, Field


class MatchedRoute(BaseModel):
    """Description of a Route used in Route search results."""

    routeCode: str | None = Field(None, description="The route code")
    name: str | None = Field(None, description="Name such as \"72\"")
    direction: str | None = Field(None, description="Inbound or Outbound")
    originationName: str | None = Field(None, description="The name of the Origin StopPoint")
    destinationName: str | None = Field(None, description="The name of the Destination StopPoint")
    originator: str | None = Field(None, description="The Id (NaPTAN code) of the Origin StopPoint")
    destination: str | None = Field(None, description="The Id (NaPTAN code) or the Destination StopPoint")
    serviceType: str | None = Field(None, description="Regular or Night")
    validTo: str | None = Field(None, description="The DateTime that the Service containing this Route is valid until.")
    validFrom: str | None = Field(None, description="The DateTime that the Service containing this Route is valid from.")

    model_config = ConfigDict(from_attributes=True)
