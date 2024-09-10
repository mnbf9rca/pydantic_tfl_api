from .Casualty import Casualty
from .Vehicle import Vehicle
from pydantic import BaseModel, Field
from typing import List, Optional


class AccidentDetail(BaseModel):
    id: Optional[int] = Field(None, alias='id')
    lat: Optional[float] = Field(None, alias='lat')
    lon: Optional[float] = Field(None, alias='lon')
    location: Optional[str] = Field(None, alias='location')
    date: Optional[str] = Field(None, alias='date')
    severity: Optional[str] = Field(None, alias='severity')
    borough: Optional[str] = Field(None, alias='borough')
    casualties: Optional[list[Casualty]] = Field(None, alias='casualties')
    vehicles: Optional[list[Vehicle]] = Field(None, alias='vehicles')

    model_config = {'from_attributes': True}
