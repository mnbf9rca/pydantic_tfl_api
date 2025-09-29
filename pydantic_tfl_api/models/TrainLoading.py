from pydantic import BaseModel, ConfigDict, Field


class TrainLoading(BaseModel):
    line: str | None = Field(None)
    lineDirection: str | None = Field(None)
    platformDirection: str | None = Field(None)
    direction: str | None = Field(None)
    naptanTo: str | None = Field(None)
    timeSlice: str | None = Field(None)
    value: int | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
