from pydantic import BaseModel, Field
from typing import Optional


class ValidityPeriod(BaseModel):
    fromDate: Optional[str] = Field(None, alias='fromDate')
    toDate: Optional[str] = Field(None, alias='toDate')
    isNow: Optional[bool] = Field(None, alias='isNow')

    class Config:
        from_attributes = True
