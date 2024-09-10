from pydantic import BaseModel, Field
from typing import Optional


class ActiveServiceType(BaseModel):
    mode: Optional[str] = Field(None, alias='mode')
    serviceType: Optional[str] = Field(None, alias='serviceType')

    model_config = {'from_attributes': True}
