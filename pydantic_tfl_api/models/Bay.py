from pydantic import BaseModel, Field
from typing import Optional


class Bay(BaseModel):
    bayType: Optional[str] = Field(None, alias='bayType')
    bayCount: Optional[int] = Field(None, alias='bayCount')
    free: Optional[int] = Field(None, alias='free')
    occupied: Optional[int] = Field(None, alias='occupied')

    model_config = {'from_attributes': True}
