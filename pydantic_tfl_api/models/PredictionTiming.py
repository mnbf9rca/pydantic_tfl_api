from pydantic import BaseModel, Field
from typing import Optional


class PredictionTiming(BaseModel):
    countdownServerAdjustment: Optional[str] = Field(None, alias='countdownServerAdjustment')
    source: Optional[str] = Field(None, alias='source')
    insert: Optional[str] = Field(None, alias='insert')
    read: Optional[str] = Field(None, alias='read')
    sent: Optional[str] = Field(None, alias='sent')
    received: Optional[str] = Field(None, alias='received')

    model_config = {'from_attributes': True}
