from pydantic import BaseModel, ConfigDict, Field

from .Disruption import Disruption
from .ValidityPeriod import ValidityPeriod


class LineStatus(BaseModel):
    id: int | None = Field(None)
    lineId: str | None = Field(None)
    statusSeverity: int | None = Field(None)
    statusSeverityDescription: str | None = Field(None)
    reason: str | None = Field(None)
    created: str | None = Field(None)
    modified: str | None = Field(None)
    validityPeriods: list[ValidityPeriod] | None = Field(None)
    disruption: Disruption | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
