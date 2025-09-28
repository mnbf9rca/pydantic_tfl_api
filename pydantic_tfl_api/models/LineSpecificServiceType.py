from .LineServiceTypeInfo import LineServiceTypeInfo
from pydantic import BaseModel, Field, ConfigDict


class LineSpecificServiceType(BaseModel):
    serviceType: LineServiceTypeInfo | None = Field(None)
    stopServesServiceType: bool | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
