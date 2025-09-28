from .ServiceFrequency import ServiceFrequency
from .TwentyFourHourClockTime import TwentyFourHourClockTime
from .TypeEnum import TypeEnum
from pydantic import BaseModel, Field, ConfigDict


class Period(BaseModel):
    type: TypeEnum | None = Field(None)
    fromTime: TwentyFourHourClockTime | None = Field(None)
    toTime: TwentyFourHourClockTime | None = Field(None)
    frequency: ServiceFrequency | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
