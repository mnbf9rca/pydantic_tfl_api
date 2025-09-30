from pydantic import BaseModel, ConfigDict, Field

from .Identifier import Identifier


class RouteOption(BaseModel):
    id: str | None = Field(None)
    name: str | None = Field(None)
    directions: list[str] | None = Field(None)
    lineIdentifier: Identifier | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
