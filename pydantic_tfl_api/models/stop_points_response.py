from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from .stop_point import StopPoint

class StopPointsResponse(BaseModel):
    stop_points: Optional[List[StopPoint]] = Field(None, alias='stopPoints')
    page_size: int = Field(alias='pageSize')
    total: int = Field(alias='total')
    page: int = Field(alias='page')
    content_expires: Optional[datetime] = Field(None)

    model_config = {'populate_by_name': True}
