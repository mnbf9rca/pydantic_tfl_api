from pydantic import BaseModel, Field
from typing import Optional


class RoadDisruptionSchedule(BaseModel):
    startTime: Optional[str] = Field(None, alias='startTime')
    endTime: Optional[str] = Field(None, alias='endTime')

    model_config = {'from_attributes': True}
