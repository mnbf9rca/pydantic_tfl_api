from pydantic import BaseModel, ConfigDict, Field

from .SearchMatch import SearchMatch


class SearchResponse(BaseModel):
    query: str | None = Field(None)
    from_field: int | None = Field(None, alias='from')
    page: int | None = Field(None)
    pageSize: int | None = Field(None)
    provider: str | None = Field(None)
    total: int | None = Field(None)
    matches: list[SearchMatch] | None = Field(None)
    maxScore: float | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
