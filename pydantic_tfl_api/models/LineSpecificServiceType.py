from .LineServiceTypeInfo import LineServiceTypeInfo
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Type


class LineSpecificServiceType(BaseModel):
    serviceType: Optional[LineServiceTypeInfo] = Field(None)
    stopServesServiceType: bool | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
