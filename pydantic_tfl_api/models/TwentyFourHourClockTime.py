from pydantic import BaseModel, Field
from typing import Optional


class TwentyFourHourClockTime(BaseModel):
    hour: Optional[str] = Field(None, alias='hour')
    minute: Optional[str] = Field(None, alias='minute')

    model_config = {'from_attributes': True}
