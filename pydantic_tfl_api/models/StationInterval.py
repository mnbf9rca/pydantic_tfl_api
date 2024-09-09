from pydantic import BaseModel, Field
from .Interval import Interval
from pydantic import BaseModel, Field
from typing import List, Optional


class StationInterval(BaseModel):
    id: Optional[str] = Field(None, alias='id')
    intervals: Optional[List[Interval]] = Field(None, alias='intervals')

    class Config:
        from_attributes = True
