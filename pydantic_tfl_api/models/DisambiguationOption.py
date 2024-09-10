from pydantic import BaseModel, Field
from typing import Optional


class DisambiguationOption(BaseModel):
    description: Optional[str] = Field(None, alias='description')
    uri: Optional[str] = Field(None, alias='uri')

    model_config = {'from_attributes': True}
