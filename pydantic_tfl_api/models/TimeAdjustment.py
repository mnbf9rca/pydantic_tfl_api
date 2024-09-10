from pydantic import BaseModel, Field
from typing import Optional


class TimeAdjustment(BaseModel):
    date: Optional[str] = Field(None, alias='date')
    time: Optional[str] = Field(None, alias='time')
    timeIs: Optional[str] = Field(None, alias='timeIs')
    uri: Optional[str] = Field(None, alias='uri')

    class Config:
        from_attributes = True
