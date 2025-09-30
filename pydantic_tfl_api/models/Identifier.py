from pydantic import BaseModel, ConfigDict, Field

from .Crowding import Crowding
from .RouteTypeEnum import RouteTypeEnum
from .StatusEnum import StatusEnum


class Identifier(BaseModel):
    id: str | None = Field(None)
    name: str | None = Field(None)
    uri: str | None = Field(None)
    fullName: str | None = Field(None)
    type: str | None = Field(None)
    crowding: Crowding | None = Field(None)
    routeType: RouteTypeEnum | None = Field(None)
    status: StatusEnum | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
