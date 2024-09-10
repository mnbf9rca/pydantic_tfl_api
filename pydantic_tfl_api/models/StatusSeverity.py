from pydantic import BaseModel, Field
from typing import Optional


class StatusSeverity(BaseModel):
    modeName: Optional[str] = Field(None, alias='modeName')
    severityLevel: Optional[int] = Field(None, alias='severityLevel')
    description: Optional[str] = Field(None, alias='description')

    model_config = {'from_attributes': True}
