from pydantic import BaseModel, ConfigDict, Field


class MatchedRoute(BaseModel):
    routeCode: str | None = Field(None)
    name: str | None = Field(None)
    direction: str | None = Field(None)
    originationName: str | None = Field(None)
    destinationName: str | None = Field(None)
    originator: str | None = Field(None)
    destination: str | None = Field(None)
    serviceType: str | None = Field(None)
    validTo: str | None = Field(None)
    validFrom: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
