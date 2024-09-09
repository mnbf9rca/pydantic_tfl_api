from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
from typing import List, Optional


class OrderedRoute(BaseModel):
    name: Optional[str] = Field(None, alias='name')
    naptanIds: Optional[List[str]] = Field(None, alias='naptanIds')
    serviceType: Optional[str] = Field(None, alias='serviceType')

    class Config:
        from_attributes = True
