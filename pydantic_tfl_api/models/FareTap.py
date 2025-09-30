from pydantic import BaseModel, ConfigDict, Field

from .FareTapDetails import FareTapDetails


class FareTap(BaseModel):
    atcoCode: str | None = Field(None)
    tapDetails: FareTapDetails | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
