from .DateTimeTypeEnum import DateTimeTypeEnum
from .TimeAdjustments import TimeAdjustments
from pydantic import BaseModel, Field
from typing import Optional, Type


class SearchCriteria(BaseModel):
    dateTime: Optional[str] = Field(None, alias='dateTime')
    dateTimeType: Optional[DateTimeTypeEnum] = Field(None, alias='dateTimeType')
    timeAdjustments: Optional[TimeAdjustments] = Field(None, alias='timeAdjustments')

    model_config = {'from_attributes': True}
