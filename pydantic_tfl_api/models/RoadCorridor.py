from pydantic import BaseModel, Field
from typing import Optional


class RoadCorridor(BaseModel):
    id: Optional[str] = Field(None, alias='id')
    displayName: Optional[str] = Field(None, alias='displayName')
    group: Optional[str] = Field(None, alias='group')
    statusSeverity: Optional[str] = Field(None, alias='statusSeverity')
    statusSeverityDescription: Optional[str] = Field(None, alias='statusSeverityDescription')
    bounds: Optional[str] = Field(None, alias='bounds')
    envelope: Optional[str] = Field(None, alias='envelope')
    statusAggregationStartDate: Optional[str] = Field(None, alias='statusAggregationStartDate')
    statusAggregationEndDate: Optional[str] = Field(None, alias='statusAggregationEndDate')
    url: Optional[str] = Field(None, alias='url')

    model_config = {'from_attributes': True}
