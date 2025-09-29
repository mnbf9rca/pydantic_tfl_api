from .FareTapDetails import FareTapDetails
from pydantic import BaseModel, Field, ConfigDict


class FareTap(BaseModel):
    atcoCode: str | None = Field(None)
    tapDetails: FareTapDetails | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
