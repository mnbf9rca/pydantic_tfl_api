from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Mode(BaseModel):
    is_tfl_service: bool = Field(alias='isTflService')
    is_fare_paying: bool = Field(alias='isFarePaying')
    is_scheduled_service: bool = Field(alias='isScheduledService')
    mode_name: str = Field(alias='modeName')
    content_expires: Optional[datetime] = Field(None)

    model_config = {'populate_by_name': True}