from pydantic import BaseModel, Field
from .FareTapDetails import FareTapDetails
from pydantic import BaseModel, Field
from typing import Optional


class FareTap(BaseModel):
    atcoCode: Optional[str] = Field(None, alias='atcoCode')
    tapDetails: Optional[FareTapDetails] = Field(None, alias='tapDetails')

    class Config:
        from_attributes = True
