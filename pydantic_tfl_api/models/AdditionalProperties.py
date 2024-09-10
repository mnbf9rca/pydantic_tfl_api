from pydantic import BaseModel, Field
from typing import Optional


class AdditionalProperties(BaseModel):
    category: Optional[str] = Field(None, alias='category')
    key: Optional[str] = Field(None, alias='key')
    sourceSystemKey: Optional[str] = Field(None, alias='sourceSystemKey')
    value: Optional[str] = Field(None, alias='value')
    modified: Optional[str] = Field(None, alias='modified')

    model_config = {'from_attributes': True}
