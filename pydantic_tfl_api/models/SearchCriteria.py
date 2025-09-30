from pydantic import BaseModel, ConfigDict, Field

from .DateTimeTypeEnum import DateTimeTypeEnum
from .TimeAdjustments import TimeAdjustments


class SearchCriteria(BaseModel):
    dateTime: str | None = Field(None)
    dateTimeType: DateTimeTypeEnum | None = Field(None)
    timeAdjustments: TimeAdjustments | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
