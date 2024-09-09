from pydantic import BaseModel, Field
from .LineSpecificServiceType import LineSpecificServiceType
from pydantic import BaseModel, Field
from typing import List, Optional, Type


class LineServiceType(BaseModel):
    lineName: Optional[str] = Field(None, alias='lineName')
    lineSpecificServiceTypes: Optional[List[LineSpecificServiceType]] = Field(None, alias='lineSpecificServiceTypes')

    class Config:
        from_attributes = True
