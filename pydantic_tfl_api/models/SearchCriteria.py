from .DateTimeTypeEnum import DateTimeTypeEnum
from .TimeAdjustments import TimeAdjustments
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Type


class SearchCriteria(BaseModel):
    dateTime: str | None = Field(None)
    dateTimeType: DateTimeTypeEnum | None = Field(None)
    timeAdjustments: Optional[TimeAdjustments] = Field(None)

    model_config = ConfigDict(from_attributes=True)
