from pydantic import BaseModel, ConfigDict, Field

from .ServiceFrequency import ServiceFrequency
from .TwentyFourHourClockTime import TwentyFourHourClockTime
from .TypeEnum import TypeEnum


class Period(BaseModel):
    type: TypeEnum | None = Field(None)
    fromTime: TwentyFourHourClockTime | None = Field(None)
    toTime: TwentyFourHourClockTime | None = Field(None)
    frequency: ServiceFrequency | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
