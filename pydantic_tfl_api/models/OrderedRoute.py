from pydantic import BaseModel, Field
from typing import List, Optional


class OrderedRoute(BaseModel):
    name: Optional[str] = Field(None, alias='name')
    naptanIds: Optional[list[str]] = Field(None, alias='naptanIds')
    serviceType: Optional[str] = Field(None, alias='serviceType')

    model_config = {'from_attributes': True}
