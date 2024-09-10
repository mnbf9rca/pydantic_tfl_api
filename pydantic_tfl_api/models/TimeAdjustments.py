from .TimeAdjustment import TimeAdjustment
from pydantic import BaseModel, Field
from typing import Optional


class TimeAdjustments(BaseModel):
    earliest: Optional[TimeAdjustment] = Field(None, alias='earliest')
    earlier: Optional[TimeAdjustment] = Field(None, alias='earlier')
    later: Optional[TimeAdjustment] = Field(None, alias='later')
    latest: Optional[TimeAdjustment] = Field(None, alias='latest')

    model_config = {'from_attributes': True}
