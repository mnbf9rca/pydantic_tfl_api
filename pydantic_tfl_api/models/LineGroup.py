from pydantic import BaseModel, ConfigDict, Field


class LineGroup(BaseModel):
    naptanIdReference: str | None = Field(None)
    stationAtcoCode: str | None = Field(None)
    lineIdentifier: list[str] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
