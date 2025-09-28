from .StreetSegment import StreetSegment
from pydantic import BaseModel, Field, ConfigDict


class Street(BaseModel):
    name: str | None = Field(None)
    closure: str | None = Field(None)
    directions: str | None = Field(None)
    segments: list[StreetSegment] | None = Field(None)
    sourceSystemId: int | None = Field(None)
    sourceSystemKey: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
