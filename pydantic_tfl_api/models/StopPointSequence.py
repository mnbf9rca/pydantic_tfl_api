from pydantic import BaseModel, ConfigDict, Field

from .MatchedStop import MatchedStop
from .ServiceTypeEnum import ServiceTypeEnum


class StopPointSequence(BaseModel):
    lineId: str | None = Field(None)
    lineName: str | None = Field(None)
    direction: str | None = Field(None)
    branchId: int | None = Field(None)
    nextBranchIds: list[int] | None = Field(None)
    prevBranchIds: list[int] | None = Field(None)
    stopPoint: list[MatchedStop] | None = Field(None)
    serviceType: ServiceTypeEnum | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
