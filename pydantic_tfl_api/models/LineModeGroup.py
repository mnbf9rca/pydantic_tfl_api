from pydantic import BaseModel, Field
from typing import List, Optional


class LineModeGroup(BaseModel):
    modeName: Optional[str] = Field(None, alias='modeName')
    lineIdentifier: Optional[list[str]] = Field(None, alias='lineIdentifier')

    class Config:
        from_attributes = True
