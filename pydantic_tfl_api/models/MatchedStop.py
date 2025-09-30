from pydantic import BaseModel, ConfigDict, Field

from .Identifier import Identifier


class MatchedStop(BaseModel):
    routeId: int | None = Field(None)
    parentId: str | None = Field(None)
    stationId: str | None = Field(None)
    icsId: str | None = Field(None)
    topMostParentId: str | None = Field(None)
    direction: str | None = Field(None)
    towards: str | None = Field(None)
    modes: list[str] | None = Field(None)
    stopType: str | None = Field(None)
    stopLetter: str | None = Field(None)
    zone: str | None = Field(None)
    accessibilitySummary: str | None = Field(None)
    hasDisruption: bool | None = Field(None)
    lines: list[Identifier] | None = Field(None)
    status: bool | None = Field(None)
    id: str | None = Field(None)
    url: str | None = Field(None)
    name: str | None = Field(None)
    lat: float | None = Field(None)
    lon: float | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
