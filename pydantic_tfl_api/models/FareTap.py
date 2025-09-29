from .FareTapDetails import FareTapDetails
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class FareTap(BaseModel):
    atcoCode: str | None = Field(None)
    tapDetails: Optional[FareTapDetails] = Field(None)

    model_config = ConfigDict(from_attributes=True)
