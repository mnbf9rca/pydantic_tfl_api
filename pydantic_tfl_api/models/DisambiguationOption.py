from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
from typing import Optional


class DisambiguationOption(BaseModel):
    description: Optional[str] = Field(None, alias='description')
    uri: Optional[str] = Field(None, alias='uri')

    class Config:
        from_attributes = True
