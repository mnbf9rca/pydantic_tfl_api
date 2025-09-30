from pydantic import BaseModel, ConfigDict, Field


class RoadCorridor(BaseModel):
    id: str | None = Field(None, description="The Id of the Corridor e.g. \"A406\"")
    displayName: str | None = Field(None, description="The display name of the Corridor e.g. \"North Circular (A406)\". This may be identical to the Id.")
    group: str | None = Field(None, description="The group name of the Corridor e.g. \"Central London\". Most corridors are not grouped, in which case this field can be null.")
    statusSeverity: str | None = Field(None, description="Standard multi-mode status severity code")
    statusSeverityDescription: str | None = Field(None, description="Description of the status severity as applied to RoadCorridors")
    bounds: str | None = Field(None, description="The Bounds of the Corridor, given by the south-east followed by the north-west co-ordinate pair in geoJSON format e.g. \"[[-1.241531,51.242151],[1.641223,53.765721]]\"")
    envelope: str | None = Field(None, description="The Envelope of the Corridor, given by the corner co-ordinates of a rectangular (four-point) polygon in geoJSON format e.g. \"[[-1.241531,51.242151],[-1.241531,53.765721],[1.641223,53.765721],[1.641223,51.242151]]\"")
    statusAggregationStartDate: str | None = Field(None, description="The start of the period over which status has been aggregated, or null if this is the current corridor status.")
    statusAggregationEndDate: str | None = Field(None, description="The end of the period over which status has been aggregated, or null if this is the current corridor status.")
    url: str | None = Field(None, description="URL to retrieve this Corridor.")

    model_config = ConfigDict(from_attributes=True)
