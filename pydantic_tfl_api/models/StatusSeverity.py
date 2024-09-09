from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
from typing import Optional


class StatusSeverity(BaseModel):
    modeName: Optional[str] = Field(None, alias='modeName')
    severityLevel: Optional[int] = Field(None, alias='severityLevel')
    description: Optional[str] = Field(None, alias='description')

    class Config:
        from_attributes = True
