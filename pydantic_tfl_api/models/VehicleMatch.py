from .ComplianceEnum import ComplianceEnum
from pydantic import BaseModel, Field
from typing import Optional


class VehicleMatch(BaseModel):
    vrm: Optional[str] = Field(None, alias='vrm')
    type: Optional[str] = Field(None, alias='type')
    make: Optional[str] = Field(None, alias='make')
    model: Optional[str] = Field(None, alias='model')
    colour: Optional[str] = Field(None, alias='colour')
    compliance: Optional[ComplianceEnum] = Field(None, alias='compliance')

    model_config = {'from_attributes': True}
