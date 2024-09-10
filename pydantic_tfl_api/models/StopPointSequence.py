from .MatchedStop import MatchedStop
from .ServiceTypeEnum import ServiceTypeEnum
from pydantic import BaseModel, Field
from typing import List, Match, Optional, Type


class StopPointSequence(BaseModel):
    lineId: Optional[str] = Field(None, alias='lineId')
    lineName: Optional[str] = Field(None, alias='lineName')
    direction: Optional[str] = Field(None, alias='direction')
    branchId: Optional[int] = Field(None, alias='branchId')
    nextBranchIds: Optional[list[int]] = Field(None, alias='nextBranchIds')
    prevBranchIds: Optional[list[int]] = Field(None, alias='prevBranchIds')
    stopPoint: Optional[list[MatchedStop]] = Field(None, alias='stopPoint')
    serviceType: Optional[ServiceTypeEnum] = Field(None, alias='serviceType')

    model_config = {'from_attributes': True}
