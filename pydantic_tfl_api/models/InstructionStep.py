from .PathAttribute import PathAttribute
from .SkyDirectionDescriptionEnum import SkyDirectionDescriptionEnum
from .TrackTypeEnum import TrackTypeEnum
from pydantic import BaseModel, Field
from typing import Optional, Type


class InstructionStep(BaseModel):
    description: Optional[str] = Field(None, alias='description')
    turnDirection: Optional[str] = Field(None, alias='turnDirection')
    streetName: Optional[str] = Field(None, alias='streetName')
    distance: Optional[int] = Field(None, alias='distance')
    cumulativeDistance: Optional[int] = Field(None, alias='cumulativeDistance')
    skyDirection: Optional[int] = Field(None, alias='skyDirection')
    skyDirectionDescription: Optional[SkyDirectionDescriptionEnum] = Field(None, alias='skyDirectionDescription')
    cumulativeTravelTime: Optional[int] = Field(None, alias='cumulativeTravelTime')
    latitude: Optional[float] = Field(None, alias='latitude')
    longitude: Optional[float] = Field(None, alias='longitude')
    pathAttribute: Optional[PathAttribute] = Field(None, alias='pathAttribute')
    descriptionHeading: Optional[str] = Field(None, alias='descriptionHeading')
    trackType: Optional[TrackTypeEnum] = Field(None, alias='trackType')

    model_config = {'from_attributes': True}
