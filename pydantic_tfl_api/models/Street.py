from .StreetSegment import StreetSegment
from pydantic import BaseModel, Field
from typing import List, Optional


class Street(BaseModel):
    name: Optional[str] = Field(None, alias='name')
    closure: Optional[str] = Field(None, alias='closure')
    directions: Optional[str] = Field(None, alias='directions')
    segments: Optional[list[StreetSegment]] = Field(None, alias='segments')
    sourceSystemId: Optional[int] = Field(None, alias='sourceSystemId')
    sourceSystemKey: Optional[str] = Field(None, alias='sourceSystemKey')

    model_config = {'from_attributes': True}
