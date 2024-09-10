from .Bay import Bay
from pydantic import BaseModel, Field
from typing import List, Optional


class CarParkOccupancy(BaseModel):
    id: Optional[str] = Field(None, alias='id')
    bays: Optional[list[Bay]] = Field(None, alias='bays')
    name: Optional[str] = Field(None, alias='name')
    carParkDetailsUrl: Optional[str] = Field(None, alias='carParkDetailsUrl')

    model_config = {'from_attributes': True}
