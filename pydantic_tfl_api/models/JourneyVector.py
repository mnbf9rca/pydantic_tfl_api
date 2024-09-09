from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
from typing import Optional


class JourneyVector(BaseModel):
    from_field: Optional[str] = Field(None, alias='from')
    to: Optional[str] = Field(None, alias='to')
    via: Optional[str] = Field(None, alias='via')
    uri: Optional[str] = Field(None, alias='uri')

    class Config:
        from_attributes = True
