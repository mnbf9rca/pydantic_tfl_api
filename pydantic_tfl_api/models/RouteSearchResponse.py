from pydantic import BaseModel, Field
from .RouteSearchMatch import RouteSearchMatch
from pydantic import BaseModel, Field
from typing import List, Match, Optional


class RouteSearchResponse(BaseModel):
    input: Optional[str] = Field(None, alias='input')
    searchMatches: Optional[List[RouteSearchMatch]] = Field(None, alias='searchMatches')

    class Config:
        from_attributes = True
