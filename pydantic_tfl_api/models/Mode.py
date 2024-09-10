from pydantic import BaseModel, Field
from typing import Optional


class Mode(BaseModel):
    isTflService: Optional[bool] = Field(None, alias='isTflService')
    isFarePaying: Optional[bool] = Field(None, alias='isFarePaying')
    isScheduledService: Optional[bool] = Field(None, alias='isScheduledService')
    modeName: Optional[str] = Field(None, alias='modeName')

    model_config = {'from_attributes': True}
