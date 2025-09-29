from .LineSpecificServiceType import LineSpecificServiceType
from pydantic import BaseModel, Field, ConfigDict


class LineServiceType(BaseModel):
    lineName: str | None = Field(None)
    lineSpecificServiceTypes: list[LineSpecificServiceType] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
