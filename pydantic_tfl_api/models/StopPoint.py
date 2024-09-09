from pydantic import BaseModel, Field
from .AdditionalProperties import AdditionalProperties
from .Identifier import Identifier
from .LineGroup import LineGroup
from .LineModeGroup import LineModeGroup
from .Place import Place
from pydantic import BaseModel, Field
from typing import List, Optional


class StopPoint(BaseModel):
    naptanId: Optional[str] = Field(None, alias='naptanId')
    platformName: Optional[str] = Field(None, alias='platformName')
    indicator: Optional[str] = Field(None, alias='indicator')
    stopLetter: Optional[str] = Field(None, alias='stopLetter')
    modes: Optional[List[str]] = Field(None, alias='modes')
    icsCode: Optional[str] = Field(None, alias='icsCode')
    smsCode: Optional[str] = Field(None, alias='smsCode')
    stopType: Optional[str] = Field(None, alias='stopType')
    stationNaptan: Optional[str] = Field(None, alias='stationNaptan')
    accessibilitySummary: Optional[str] = Field(None, alias='accessibilitySummary')
    hubNaptanCode: Optional[str] = Field(None, alias='hubNaptanCode')
    lines: Optional[List[Identifier]] = Field(None, alias='lines')
    lineGroup: Optional[List[LineGroup]] = Field(None, alias='lineGroup')
    lineModeGroups: Optional[List[LineModeGroup]] = Field(None, alias='lineModeGroups')
    fullName: Optional[str] = Field(None, alias='fullName')
    naptanMode: Optional[str] = Field(None, alias='naptanMode')
    status: Optional[bool] = Field(None, alias='status')
    id: Optional[str] = Field(None, alias='id')
    url: Optional[str] = Field(None, alias='url')
    commonName: Optional[str] = Field(None, alias='commonName')
    distance: Optional[float] = Field(None, alias='distance')
    placeType: Optional[str] = Field(None, alias='placeType')
    additionalProperties: Optional[List[AdditionalProperties]] = Field(None, alias='additionalProperties')
    children: 'Optional[List[Place]]' = Field(None, alias='children')
    childrenUrls: Optional[List[str]] = Field(None, alias='childrenUrls')
    lat: Optional[float] = Field(None, alias='lat')
    lon: Optional[float] = Field(None, alias='lon')

    class Config:
        from_attributes = True
