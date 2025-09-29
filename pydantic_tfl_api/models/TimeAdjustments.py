from .TimeAdjustment import TimeAdjustment
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class TimeAdjustments(BaseModel):
    earliest: Optional[TimeAdjustment] = Field(None)
    earlier: Optional[TimeAdjustment] = Field(None)
    later: Optional[TimeAdjustment] = Field(None)
    latest: Optional[TimeAdjustment] = Field(None)

    model_config = ConfigDict(from_attributes=True)
