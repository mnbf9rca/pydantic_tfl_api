from pydantic import BaseModel, Field
from .Identifier import Identifier
from pydantic import BaseModel, Field
from typing import List, Optional


class RouteOption(BaseModel):
    id: Optional[str] = Field(None, alias='id')
    name: Optional[str] = Field(None, alias='name')
    directions: Optional[List[str]] = Field(None, alias='directions')
    lineIdentifier: Optional[Identifier] = Field(None, alias='lineIdentifier')

    class Config:
        from_attributes = True
