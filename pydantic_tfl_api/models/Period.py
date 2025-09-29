from .ServiceFrequency import ServiceFrequency
from .TwentyFourHourClockTime import TwentyFourHourClockTime
from .TypeEnum import TypeEnum
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Type


class Period(BaseModel):
    type: TypeEnum | None = Field(None)
    fromTime: Optional[TwentyFourHourClockTime] = Field(None)
    toTime: Optional[TwentyFourHourClockTime] = Field(None)
    frequency: Optional[ServiceFrequency] = Field(None)

    model_config = ConfigDict(from_attributes=True)
