from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
from typing import Optional


class TwentyFourHourClockTime(BaseModel):
    hour: Optional[str] = Field(None, alias='hour')
    minute: Optional[str] = Field(None, alias='minute')

    class Config:
        from_attributes = True
