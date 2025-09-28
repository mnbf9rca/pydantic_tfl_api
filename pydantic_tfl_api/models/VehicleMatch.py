from .ComplianceEnum import ComplianceEnum
from pydantic import BaseModel, Field, ConfigDict


class VehicleMatch(BaseModel):
    vrm: str | None = Field(None)
    type: str | None = Field(None)
    make: str | None = Field(None)
    model: str | None = Field(None)
    colour: str | None = Field(None)
    compliance: ComplianceEnum | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
