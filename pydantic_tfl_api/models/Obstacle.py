from pydantic import BaseModel, Field
from typing import Optional


class Obstacle(BaseModel):
    type: Optional[str] = Field(None, alias='type')
    incline: Optional[str] = Field(None, alias='incline')
    stopId: Optional[int] = Field(None, alias='stopId')
    position: Optional[str] = Field(None, alias='position')

    model_config = {'from_attributes': True}
