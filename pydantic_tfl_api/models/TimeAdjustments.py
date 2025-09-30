from pydantic import BaseModel, ConfigDict, Field

from .TimeAdjustment import TimeAdjustment


class TimeAdjustments(BaseModel):
    earliest: TimeAdjustment | None = Field(None)
    earlier: TimeAdjustment | None = Field(None)
    later: TimeAdjustment | None = Field(None)
    latest: TimeAdjustment | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
