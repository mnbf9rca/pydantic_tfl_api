from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
from typing import Optional


class MatchedRouteSections(BaseModel):
    id: Optional[int] = Field(None, alias='id')

    class Config:
        from_attributes = True
