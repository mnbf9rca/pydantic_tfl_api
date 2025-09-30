from pydantic import BaseModel, ConfigDict, Field


class DisruptedPoint(BaseModel):
    atcoCode: str | None = Field(None)
    fromDate: str | None = Field(None)
    toDate: str | None = Field(None)
    description: str | None = Field(None)
    commonName: str | None = Field(None)
    type: str | None = Field(None)
    mode: str | None = Field(None)
    stationAtcoCode: str | None = Field(None)
    appearance: str | None = Field(None)
    additionalInformation: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
