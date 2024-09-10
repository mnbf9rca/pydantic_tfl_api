from pydantic import BaseModel, Field
from typing import List, Optional


class PlaceCategory(BaseModel):
    category: Optional[str] = Field(None, alias='category')
    availableKeys: Optional[list[str]] = Field(None, alias='availableKeys')

    model_config = {'from_attributes': True}
