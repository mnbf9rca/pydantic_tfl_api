from pydantic import BaseModel, ConfigDict, Field

from .LineSpecificServiceType import LineSpecificServiceType


class LineServiceType(BaseModel):
    lineName: str | None = Field(None)
    lineSpecificServiceTypes: list[LineSpecificServiceType] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
