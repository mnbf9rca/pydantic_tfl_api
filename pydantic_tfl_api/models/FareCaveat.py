from pydantic import BaseModel, Field
from typing import Optional


class FareCaveat(BaseModel):
    text: Optional[str] = Field(None, alias='text')
    type: Optional[str] = Field(None, alias='type')

    model_config = {'from_attributes': True}
