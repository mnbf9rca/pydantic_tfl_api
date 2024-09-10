from pydantic import BaseModel, Field
from typing import Optional


class ChargeConnectorOccupancy(BaseModel):
    id: Optional[int] = Field(None, alias='id')
    sourceSystemPlaceId: Optional[str] = Field(None, alias='sourceSystemPlaceId')
    status: Optional[str] = Field(None, alias='status')

    model_config = {'from_attributes': True}
