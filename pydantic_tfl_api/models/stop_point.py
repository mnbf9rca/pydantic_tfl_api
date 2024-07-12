from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


from .line_group import LineGroup
from .line_mode_group import LineModeGroup
from .additional_properties import AdditionalProperties
# note additional import from .line import Line
# at the end of the file

class StopPoint(BaseModel):
    naptan_id: str = Field(alias="naptanId")
    platform_name: Optional[str] = Field(None, alias="platformName")
    indicator: Optional[str] = Field(None, alias="indicator")
    stop_letter: Optional[str] = Field(None, alias="stopLetter")
    modes: List[str] = Field(alias="modes")
    ics_code: Optional[str] = Field(None, alias="icsCode")
    sms_code: Optional[str] = Field(None, alias="smsCode")
    stop_type: Optional[str] = Field(None, alias="stopType")
    station_naptan: str = Field(alias="stationNaptan")
    accessibility_summary: Optional[str] = Field(None, alias="accessibilitySummary")
    hub_naptan_code: Optional[str] = Field(None, alias="hubNaptanCode")
    lines: List["Line"] = Field(alias="lines")
    line_group: List[LineGroup] = Field(alias="lineGroup")
    line_mode_groups: List[LineModeGroup] = Field(alias="lineModeGroups")
    full_name: Optional[str] = Field(None, alias="fullName")
    naptan_mode: Optional[str] = Field(None, alias="naptanMode")
    status: bool = Field(alias="status")
    id: str = Field(alias="id")
    url: Optional[str] = Field(None, alias="url")
    common_name: str = Field(alias="commonName")
    distance: Optional[int] = Field(None, alias="distance")
    place_type: str = Field(alias="placeType")
    additional_properties: List[AdditionalProperties] = Field(
        alias="additionalProperties"
    )
    children: Optional[List["StopPoint"]] = Field(None, alias="children")
    children_urls: Optional[List[str]] = Field([], alias="childrenUrls")
    lat: float = Field(alias="lat")
    lon: float = Field(alias="lon")
    content_expires: Optional[datetime] = Field(None)

    model_config = {"populate_by_name": True}


# we have to import Line after StopPoint is defined or we get a circular reference
from .line import Line  # noqa: E402

# Rebuild the model to reference Line
StopPoint.model_rebuild()
