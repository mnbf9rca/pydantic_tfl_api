from pydantic import BaseModel, ConfigDict, Field


class RoadCorridor(BaseModel):
    id: str | None = Field(None)
    displayName: str | None = Field(None)
    group: str | None = Field(None)
    statusSeverity: str | None = Field(None)
    statusSeverityDescription: str | None = Field(None)
    bounds: str | None = Field(None)
    envelope: str | None = Field(None)
    statusAggregationStartDate: str | None = Field(None)
    statusAggregationEndDate: str | None = Field(None)
    url: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
