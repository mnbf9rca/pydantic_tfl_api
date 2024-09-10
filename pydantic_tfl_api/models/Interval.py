from pydantic import BaseModel, Field
from typing import Optional


class Interval(BaseModel):
    stopId: Optional[str] = Field(None, alias='stopId')
    timeToArrival: Optional[float] = Field(None, alias='timeToArrival')

    model_config = {'from_attributes': True}
