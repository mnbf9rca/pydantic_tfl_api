from .Disruption import Disruption
from .ValidityPeriod import ValidityPeriod
from pydantic import BaseModel, Field
from typing import List, Optional


class LineStatus(BaseModel):
    id: Optional[int] = Field(None, alias='id')
    lineId: Optional[str] = Field(None, alias='lineId')
    statusSeverity: Optional[int] = Field(None, alias='statusSeverity')
    statusSeverityDescription: Optional[str] = Field(None, alias='statusSeverityDescription')
    reason: Optional[str] = Field(None, alias='reason')
    created: Optional[str] = Field(None, alias='created')
    modified: Optional[str] = Field(None, alias='modified')
    validityPeriods: Optional[list[ValidityPeriod]] = Field(None, alias='validityPeriods')
    disruption: Optional[Disruption] = Field(None, alias='disruption')

    model_config = {'from_attributes': True}
