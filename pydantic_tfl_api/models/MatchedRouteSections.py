from pydantic import BaseModel, Field
from typing import Optional


class MatchedRouteSections(BaseModel):
    id: Optional[int] = Field(None, alias='id')

    model_config = {'from_attributes': True}
