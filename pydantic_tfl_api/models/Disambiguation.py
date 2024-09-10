from .DisambiguationOption import DisambiguationOption
from pydantic import BaseModel, Field
from typing import List, Optional


class Disambiguation(BaseModel):
    disambiguationOptions: Optional[list[DisambiguationOption]] = Field(None, alias='disambiguationOptions')

    class Config:
        from_attributes = True
