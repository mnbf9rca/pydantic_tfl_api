from pydantic import BaseModel, ConfigDict, Field


class StreetSegment(BaseModel):
    toid: str | None = Field(None, description="A 16 digit unique integer identifying a OS ITN (Ordnance Survey Integrated Transport Network) road link.")
    lineString: str | None = Field(None, description="geoJSON formatted LineString containing two latitude/longitude (WGS84) pairs that identify the start and end points of the street segment.")
    sourceSystemId: int | None = Field(None, description="The ID from the source system of the disruption that this street belongs to.")
    sourceSystemKey: str | None = Field(None, description="The key of the source system of the disruption that this street belongs to.")

    model_config = ConfigDict(from_attributes=True)
