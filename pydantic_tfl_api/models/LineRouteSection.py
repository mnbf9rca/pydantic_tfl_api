from pydantic import BaseModel, ConfigDict, Field


class LineRouteSection(BaseModel):
    routeId: int | None = Field(None)
    direction: str | None = Field(None)
    destination: str | None = Field(None)
    fromStation: str | None = Field(None)
    toStation: str | None = Field(None)
    serviceType: str | None = Field(None)
    vehicleDestinationText: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
