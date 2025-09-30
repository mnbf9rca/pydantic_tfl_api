from pydantic import BaseModel, ConfigDict, Field

from .AdditionalProperties import AdditionalProperties
from .Identifier import Identifier
from .LineGroup import LineGroup
from .LineModeGroup import LineModeGroup
from .Place import Place


class StopPoint(BaseModel):
    naptanId: str | None = Field(None)
    platformName: str | None = Field(None)
    indicator: str | None = Field(None, description="The indicator of the stop point e.g. \"Stop K\"")
    stopLetter: str | None = Field(None, description="The stop letter, if it could be cleansed from the Indicator e.g. \"K\"")
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
    id: str | None = Field(None, description="A unique identifier.")
    url: str | None = Field(None, description="The unique location of this resource.")
    commonName: str | None = Field(None, description="A human readable name.")
    distance: float | None = Field(None, description="The distance of the place from its search point, if this is the result of a geographical search, otherwise zero.")
    placeType: str | None = Field(None, description="The type of Place. See /Place/Meta/placeTypes for possible values.")
    additionalProperties: list[AdditionalProperties] | None = Field(None, description="A bag of additional key/value pairs with extra information about this place.")
    children: list['Place'] | None = Field(None)
    childrenUrls: list[str] | None = Field(None)
    lat: float | None = Field(None, description="WGS84 latitude of the location.")
    lon: float | None = Field(None, description="WGS84 longitude of the location.")

    model_config = ConfigDict(from_attributes=True)
