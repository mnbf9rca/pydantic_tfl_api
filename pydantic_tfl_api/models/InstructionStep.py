from pydantic import BaseModel, ConfigDict, Field

from .PathAttribute import PathAttribute
from .SkyDirectionDescriptionEnum import SkyDirectionDescriptionEnum
from .TrackTypeEnum import TrackTypeEnum


class InstructionStep(BaseModel):
    description: str | None = Field(None)
    turnDirection: str | None = Field(None)
    streetName: str | None = Field(None)
    distance: int | None = Field(None)
    cumulativeDistance: int | None = Field(None)
    skyDirection: int | None = Field(None)
    skyDirectionDescription: SkyDirectionDescriptionEnum | None = Field(None)
    cumulativeTravelTime: int | None = Field(None)
    latitude: float | None = Field(None)
    longitude: float | None = Field(None)
    pathAttribute: PathAttribute | None = Field(None)
    descriptionHeading: str | None = Field(None)
    trackType: TrackTypeEnum | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
