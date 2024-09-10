from pydantic import BaseModel, Field
from typing import Optional


class Vehicle(BaseModel):
    type: Optional[str] = Field(None, alias='type')

    class Config:
        from_attributes = True
