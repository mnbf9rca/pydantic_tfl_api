from pydantic import BaseModel, ConfigDict, Field


class StopPointRouteSection(BaseModel):
    naptanId: str | None = Field(None)
    lineId: str | None = Field(None)
    mode: str | None = Field(None)
    validFrom: str | None = Field(None)
    validTo: str | None = Field(None)
    direction: str | None = Field(None)
    routeSectionName: str | None = Field(None)
    lineString: str | None = Field(None)
    isActive: bool | None = Field(None)
    serviceType: str | None = Field(None)
    vehicleDestinationText: str | None = Field(None)
    destinationName: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
