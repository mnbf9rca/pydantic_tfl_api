from .Disruption import Disruption
from .ValidityPeriod import ValidityPeriod
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class LineStatus(BaseModel):
    id: int | None = Field(None)
    lineId: str | None = Field(None)
    statusSeverity: int | None = Field(None)
    statusSeverityDescription: str | None = Field(None)
    reason: str | None = Field(None)
    created: str | None = Field(None)
    modified: str | None = Field(None)
    validityPeriods: list[ValidityPeriod] | None = Field(None)
    disruption: Optional[Disruption] = Field(None)

    model_config = ConfigDict(from_attributes=True)
