from pydantic import BaseModel, Field
from typing import Optional


class StreetSegment(BaseModel):
    toid: Optional[str] = Field(None, alias='toid')
    lineString: Optional[str] = Field(None, alias='lineString')
    sourceSystemId: Optional[int] = Field(None, alias='sourceSystemId')
    sourceSystemKey: Optional[str] = Field(None, alias='sourceSystemKey')

    model_config = {'from_attributes': True}
