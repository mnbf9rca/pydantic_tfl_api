from pydantic import BaseModel, ConfigDict, Field

from .RouteSearchMatch import RouteSearchMatch


class RouteSearchResponse(BaseModel):
    input: str | None = Field(None)
    searchMatches: list[RouteSearchMatch] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
