from pydantic import BaseModel, Field
from typing import Optional


class LiftDisruption(BaseModel):
    icsCode: Optional[str] = Field(None, alias='icsCode')
    naptanCode: Optional[str] = Field(None, alias='naptanCode')
    stopPointName: Optional[str] = Field(None, alias='stopPointName')
    outageStartArea: Optional[str] = Field(None, alias='outageStartArea')
    outageEndArea: Optional[str] = Field(None, alias='outageEndArea')
    message: Optional[str] = Field(None, alias='message')

    model_config = {'from_attributes': True}
