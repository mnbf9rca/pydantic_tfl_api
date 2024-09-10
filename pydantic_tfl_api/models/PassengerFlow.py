from pydantic import BaseModel, Field
from typing import Optional


class PassengerFlow(BaseModel):
    timeSlice: Optional[str] = Field(None, alias='timeSlice')
    value: Optional[int] = Field(None, alias='value')

    class Config:
        from_attributes = True
