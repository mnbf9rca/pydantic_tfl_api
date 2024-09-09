from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
from typing import Optional


class LineServiceTypeInfo(BaseModel):
    name: Optional[str] = Field(None, alias='name')
    uri: Optional[str] = Field(None, alias='uri')

    class Config:
        from_attributes = True
