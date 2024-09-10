from pydantic import BaseModel, Field
from typing import Optional


class TrainLoading(BaseModel):
    line: Optional[str] = Field(None, alias='line')
    lineDirection: Optional[str] = Field(None, alias='lineDirection')
    platformDirection: Optional[str] = Field(None, alias='platformDirection')
    direction: Optional[str] = Field(None, alias='direction')
    naptanTo: Optional[str] = Field(None, alias='naptanTo')
    timeSlice: Optional[str] = Field(None, alias='timeSlice')
    value: Optional[int] = Field(None, alias='value')

    model_config = {'from_attributes': True}
