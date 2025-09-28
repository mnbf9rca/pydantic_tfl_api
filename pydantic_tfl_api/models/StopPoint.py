from .AdditionalProperties import AdditionalProperties
from .Identifier import Identifier
from .LineGroup import LineGroup
from .LineModeGroup import LineModeGroup
from .Place import Place
from pydantic import BaseModel, Field, ConfigDict


class StopPoint(BaseModel):
    naptanId: str | None = Field(None)
    platformName: str | None = Field(None)
    indicator: str | None = Field(None)
    stopLetter: str | None = Field(None)
    modes: list[str] | None = Field(None)
    icsCode: str | None = Field(None)
    smsCode: str | None = Field(None)
    stopType: str | None = Field(None)
    stationNaptan: str | None = Field(None)
    accessibilitySummary: str | None = Field(None)
    hubNaptanCode: str | None = Field(None)
    lines: list[Identifier] | None = Field(None)
    lineGroup: list[LineGroup] | None = Field(None)
    lineModeGroups: list[LineModeGroup] | None = Field(None)
    fullName: str | None = Field(None)
    naptanMode: str | None = Field(None)
    status: bool | None = Field(None)
    id: str | None = Field(None)
    url: str | None = Field(None)
    commonName: str | None = Field(None)
    distance: float | None = Field(None)
    placeType: str | None = Field(None)
    additionalProperties: list[AdditionalProperties] | None = Field(None)
    children: list['Place'] | None = Field(None)
    childrenUrls: list[str] | None = Field(None)
    lat: float | None = Field(None)
    lon: float | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
