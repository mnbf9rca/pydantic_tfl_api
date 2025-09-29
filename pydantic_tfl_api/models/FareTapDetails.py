from pydantic import BaseModel, ConfigDict, Field


class FareTapDetails(BaseModel):
    modeType: str | None = Field(None)
    validationType: str | None = Field(None)
    hostDeviceType: str | None = Field(None)
    busRouteId: str | None = Field(None)
    nationalLocationCode: int | None = Field(None)
    tapTimestamp: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
