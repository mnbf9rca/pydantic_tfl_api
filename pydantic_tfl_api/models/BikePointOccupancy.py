from pydantic import BaseModel, Field
from typing import Optional


class BikePointOccupancy(BaseModel):
    id: Optional[str] = Field(None, alias='id')
    name: Optional[str] = Field(None, alias='name')
    bikesCount: Optional[int] = Field(None, alias='bikesCount')
    emptyDocks: Optional[int] = Field(None, alias='emptyDocks')
    totalDocks: Optional[int] = Field(None, alias='totalDocks')

    model_config = {'from_attributes': True}
