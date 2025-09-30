from pydantic import BaseModel, ConfigDict, Field

from .MatchedStop import MatchedStop
from .ServiceTypeEnum import ServiceTypeEnum


class StopPointSequence(BaseModel):
    lineId: str | None = Field(None)
    lineName: str | None = Field(None)
    direction: str | None = Field(None)
    branchId: int | None = Field(None, description="The id of this branch.")
    nextBranchIds: list[int] | None = Field(None, description="The ids of the next branch(es) in the sequence. Note that the next and previous branch id can be identical in the case of a looped route e.g. the Circle line.")
    prevBranchIds: list[int] | None = Field(None, description="The ids of the previous branch(es) in the sequence. Note that the next and previous branch id can be identical in the case of a looped route e.g. the Circle line.")
    stopPoint: list[MatchedStop] | None = Field(None)
    serviceType: ServiceTypeEnum | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
