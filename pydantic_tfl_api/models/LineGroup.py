from pydantic import BaseModel, Field
from typing import List, Optional


class LineGroup(BaseModel):
    naptanIdReference: Optional[str] = Field(None, alias='naptanIdReference')
    stationAtcoCode: Optional[str] = Field(None, alias='stationAtcoCode')
    lineIdentifier: Optional[list[str]] = Field(None, alias='lineIdentifier')

    model_config = {'from_attributes': True}
