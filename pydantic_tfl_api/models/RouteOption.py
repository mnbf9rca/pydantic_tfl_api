from .Identifier import Identifier
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class RouteOption(BaseModel):
    id: str | None = Field(None)
    name: str | None = Field(None)
    directions: list[str] | None = Field(None)
    lineIdentifier: Optional[Identifier] = Field(None)

    model_config = ConfigDict(from_attributes=True)
