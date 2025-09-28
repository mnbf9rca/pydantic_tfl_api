from pydantic import BaseModel, Field, ConfigDict


class PlannedWork(BaseModel):
    id: str | None = Field(None)
    description: str | None = Field(None)
    createdDateTime: str | None = Field(None)
    lastUpdateDateTime: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
