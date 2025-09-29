from .DateTimeTypeEnum import DateTimeTypeEnum
from .TimeAdjustments import TimeAdjustments
from pydantic import BaseModel, Field, ConfigDict


class SearchCriteria(BaseModel):
    dateTime: str | None = Field(None)
    dateTimeType: DateTimeTypeEnum | None = Field(None)
    timeAdjustments: TimeAdjustments | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
