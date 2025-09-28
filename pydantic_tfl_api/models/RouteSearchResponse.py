from .RouteSearchMatch import RouteSearchMatch
from pydantic import BaseModel, Field, ConfigDict
from typing import Match


class RouteSearchResponse(BaseModel):
    input: str | None = Field(None)
    searchMatches: list[RouteSearchMatch] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
