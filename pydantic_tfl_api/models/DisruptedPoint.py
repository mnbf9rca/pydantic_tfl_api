from pydantic import BaseModel, Field
from typing import Optional


class DisruptedPoint(BaseModel):
    atcoCode: Optional[str] = Field(None, alias='atcoCode')
    fromDate: Optional[str] = Field(None, alias='fromDate')
    toDate: Optional[str] = Field(None, alias='toDate')
    description: Optional[str] = Field(None, alias='description')
    commonName: Optional[str] = Field(None, alias='commonName')
    type: Optional[str] = Field(None, alias='type')
    mode: Optional[str] = Field(None, alias='mode')
    stationAtcoCode: Optional[str] = Field(None, alias='stationAtcoCode')
    appearance: Optional[str] = Field(None, alias='appearance')
    additionalInformation: Optional[str] = Field(None, alias='additionalInformation')

    model_config = {'from_attributes': True}
