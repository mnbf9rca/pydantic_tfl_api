from pydantic import BaseModel, Field
from .LineServiceTypeInfo import LineServiceTypeInfo
from pydantic import BaseModel, Field
from typing import Optional, Type


class LineSpecificServiceType(BaseModel):
    serviceType: Optional[LineServiceTypeInfo] = Field(None, alias='serviceType')
    stopServesServiceType: Optional[bool] = Field(None, alias='stopServesServiceType')

    class Config:
        from_attributes = True
