from pydantic import BaseModel, Field, ConfigDict


class StreetSegment(BaseModel):
    toid: str | None = Field(None)
    lineString: str | None = Field(None)
    sourceSystemId: int | None = Field(None)
    sourceSystemKey: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
