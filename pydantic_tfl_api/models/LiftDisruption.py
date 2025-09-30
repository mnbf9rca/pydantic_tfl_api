from pydantic import BaseModel, ConfigDict, Field


class LiftDisruption(BaseModel):
    icsCode: str | None = Field(None)
    naptanCode: str | None = Field(None)
    stopPointName: str | None = Field(None)
    outageStartArea: str | None = Field(None)
    outageEndArea: str | None = Field(None)
    message: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
