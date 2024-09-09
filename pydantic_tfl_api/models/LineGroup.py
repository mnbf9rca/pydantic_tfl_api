from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
from typing import List, Optional


class LineGroup(BaseModel):
    naptanIdReference: Optional[str] = Field(None, alias='naptanIdReference')
    stationAtcoCode: Optional[str] = Field(None, alias='stationAtcoCode')
    lineIdentifier: Optional[List[str]] = Field(None, alias='lineIdentifier')

    class Config:
        from_attributes = True
