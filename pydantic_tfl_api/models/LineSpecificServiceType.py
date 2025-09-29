from pydantic import BaseModel, ConfigDict, Field

from .LineServiceTypeInfo import LineServiceTypeInfo


class LineSpecificServiceType(BaseModel):
    serviceType: LineServiceTypeInfo | None = Field(None)
    stopServesServiceType: bool | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
