from pydantic import BaseModel, Field
from typing import Optional


class PathAttribute(BaseModel):
    name: Optional[str] = Field(None, alias='name')
    value: Optional[str] = Field(None, alias='value')

    model_config = {'from_attributes': True}
