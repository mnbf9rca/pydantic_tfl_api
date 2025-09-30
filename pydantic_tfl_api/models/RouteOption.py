from pydantic import BaseModel, ConfigDict, Field

from .Identifier import Identifier


class RouteOption(BaseModel):
    id: str | None = Field(None, description="The Id of the route")
    name: str | None = Field(None, description="Name such as \"72\"")
    directions: list[str] | None = Field(None)
    lineIdentifier: Identifier | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
