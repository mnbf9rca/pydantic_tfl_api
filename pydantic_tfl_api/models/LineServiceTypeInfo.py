from pydantic import BaseModel, Field
from typing import Optional


class LineServiceTypeInfo(BaseModel):
    name: Optional[str] = Field(None, alias='name')
    uri: Optional[str] = Field(None, alias='uri')

    model_config = {'from_attributes': True}
